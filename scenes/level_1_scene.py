import pygame
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import os
import threading
from keras.models import load_model
from save_manager import save_score
from player import PlayerData

pose = mp.solutions.pose.Pose()

class Level1Scene:
    def __init__(self, screen, player_name):
        self.screen = screen
        # Đặt kích thước cố định cho screen
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.screen_width)
        self.cap.set(4, self.screen_height)
        model_path = 'model/model_7.h5'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        try:
            self.model = load_model(model_path)
        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")
        self.classes = ['knee_raise', 'forward_bend', 'arms_crossed', 'arms_legs_combined',
                        'leg_extension', 'arms_raised', 'arms_sideways', 'arms_front_chest',
                        'chest_exercise', 'arms_rotation']
        self.exercises = np.random.choice(self.classes, 3, replace=False).tolist()
        self.lm_list = []
        self.label = "Unknown"
        self.score = 0  # Điểm của động tác hiện tại
        self.total_score = 0  # Tổng điểm của cả level
        self.current_exercise_index = 0
        self.correct_count = 0  # Đếm số lần nhận diện đúng cho động tác hiện tại
        self.required_correct_count = 10  # Số lần nhận diện đúng cần để đạt 100 điểm
        self._is_done = False
        self.font = pygame.font.Font(None, 36)
        self.last_score_time = 0  # Thời gian cuối cùng cộng điểm
        self.COOLDOWN_MS = 5000  # Thời gian chờ 5 giây
        # Khởi tạo background
        self.bg = cv2.imread("assets/images/level1_bg.png")
        if self.bg is None:
            raise FileNotFoundError("Background image not found at: assets/images/level1_bg.png")
        self.bg = cv2.cvtColor(self.bg, cv2.COLOR_BGR2RGB)  # Chuyển sang RGB
        self.bg = cv2.resize(self.bg, (self.screen_width, self.screen_height))
        # Khởi tạo video cho từng exercise với FPS
        self.videos = {}
        for exercise in self.exercises:
            for ext in ['.mov', '.mp4']:
                video_path = f"assets/videos/{exercise}{ext}"
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    self.videos[exercise] = cap
                    cap.set(cv2.CAP_PROP_FPS, cap.get(cv2.CAP_PROP_FPS))  # Đặt FPS gốc
                    # print(f"DEBUG: Loaded video for {exercise} at {video_path}, FPS: {cap.get(cv2.CAP_PROP_FPS)}")
                    break
            if exercise not in self.videos:
                raise FileNotFoundError(f"Video not found for {exercise} (.mov or .mp4)")
        self.start_time = pygame.time.get_ticks()  # Thời gian bắt đầu
        self.player_name = player_name  # Lưu tên người chơi
        self.exercise_times = []  # Lưu thời gian từng động tác
        self.last_frame_time = 0  # Thời gian hiển thị frame cuối cùng
        self.score_sound = pygame.mixer.Sound("assets/sounds/bell_3.mp3")
        self.next_ex_sound = pygame.mixer.Sound("assets/sounds/woosh.mp3")
        self.plus_ten_image = pygame.image.load("assets/images/plus.png").convert_alpha()
        self.show_plus_ten = False
        self.plus_ten_start_time = 0
        self.congrat_image = pygame.image.load("assets/images/khen.png").convert_alpha()
        self.congrat_image = pygame.transform.scale(self.congrat_image, (800, 400)) 
        self.show_congrat = False
        self.congrat_start_time = 0
        self.waiting_for_next_exercise = False  # Trạng thái chờ chuyển động tác
        self.sound_played = False  # Trạng thái âm thanh đã phát

    def make_landmark_timestep(self, results):
        lm_list = []
        landmarks = results.pose_landmarks.landmark
        base_x, base_y, base_z = landmarks[0].x, landmarks[0].y, landmarks[0].z
        center_x = np.mean([lm.x for lm in landmarks])
        center_y = np.mean([lm.y for lm in landmarks])
        center_z = np.mean([lm.z for lm in landmarks])
        distances = [np.sqrt((lm.x - center_x)**2 + (lm.y - center_y)**2 + (lm.z - center_z)**2) for lm in landmarks[1:]]
        scale_factors = [1.0 / dist if dist > 0 else 1.0 for dist in distances]
        lm_list.extend([0.0, 0.0, 0.0, landmarks[0].visibility])
        for lm, scale_factor in zip(landmarks[1:], scale_factors):
            lm_list.extend([(lm.x - base_x) * scale_factor, (lm.y - base_y) * scale_factor, (lm.z - base_z) * scale_factor, lm.visibility])
        return lm_list

    def detect(self):
        if len(self.lm_list) == 7:
            lm_array = np.array(self.lm_list)
            lm_array = np.expand_dims(lm_array, axis=0)
            results = self.model.predict(lm_array)
            predicted_label_index = np.argmax(results, axis=1)[0]
            confidence = np.max(results, axis=1)[0]
            
            self.label = self.classes[predicted_label_index] if confidence > 0.95 else "neutral"
            current_time = pygame.time.get_ticks()
            current_exercise = self.exercises[self.current_exercise_index]
            
            if self.label == current_exercise and confidence > 0.95:
                if current_time - self.last_score_time >= self.COOLDOWN_MS:
                    self.correct_count += 1
                    self.score += 10  # Cộng 10 điểm sau mỗi 5 giây
                    self.last_score_time = current_time
                    self.score_sound.play()
                    self.show_plus_ten = True  # Hiển thị hình ảnh +10
                    self.plus_ten_start_time = current_time  # Ghi thời gian bắt đầu
                    # print(f"DEBUG: Correct detection - Count: {self.correct_count}, Score: {self.score}, Total Score: {self.total_score}")
            
            if self.correct_count >= self.required_correct_count and not self.waiting_for_next_exercise:  # Đạt 100 điểm và chưa chờ
                self.total_score += self.score
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - self.start_time) / 1000
                self.exercise_times.append(elapsed_time)
                if not self.sound_played:  # Phát âm thanh chỉ 1 lần
                    self.next_ex_sound.play()
                    self.sound_played = True
                self.show_congrat = True  # Hiển thị hình ảnh chúc mừng
                self.congrat_start_time = current_time  # Ghi thời gian bắt đầu
                self.waiting_for_next_exercise = True  # Đánh dấu chờ chuyển động tác
                # print(f"DEBUG: Waiting for next exercise - Index: {self.current_exercise_index}, Total Score: {self.total_score}, Exercise Time: {elapsed_time}s")
            self.lm_list = []

    def draw_landmark_on_image(self, results, frame):
        return frame

    def handle_event(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            current_time = pygame.time.get_ticks()
            if self.current_exercise_index < len(self.exercises):
                elapsed_time = (current_time - self.start_time) / 1000
                self.exercise_times.append(elapsed_time)
            total_time = sum(self.exercise_times)
            final_score = self.total_score + self.score
            player = PlayerData(self.player_name, final_score, total_time, "Level 1")
            # print(f"DEBUG: Saving score - Player: {self.player_name}, Final Score: {final_score}, Total Time: {total_time}s")
            save_score(player)
            self._is_done = True

    def update(self):
        current_time = pygame.time.get_ticks()
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            # print("DEBUG: Camera frame shape:", frame.shape, "dtype:", frame.dtype)
            if frame.shape[2] == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_I420)
            results = pose.process(frame_rgb)
            if results.pose_landmarks:
                lm = self.make_landmark_timestep(results)
                self.lm_list.append(lm)
                if len(self.lm_list) == 7:
                    detect_thread = threading.Thread(target=self.detect)
                    detect_thread.start()
                    self.lm_list = []
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            display_frame = self.bg.copy()
            if self.current_exercise_index < len(self.exercises):
                current_exercise = self.exercises[self.current_exercise_index]
                cap = self.videos[current_exercise]
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps > 0:
                    frame_time = 1000 / fps
                    if current_time - self.last_frame_time >= frame_time:
                        ret_video, video_frame = cap.read()
                        if ret_video:
                            video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
                            video_frame = cv2.resize(video_frame, (253, 450))
                            x_offset = 50
                            y_offset = 185
                            display_frame[y_offset:y_offset+450, x_offset:x_offset+253] = video_frame
                        else:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        self.last_frame_time = current_time
                else:
                    ret_video, video_frame = cap.read()
                    if ret_video:
                        video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
                        video_frame = cv2.resize(video_frame, (253, 450))
                        x_offset = 50
                        y_offset = 185
                        display_frame[y_offset:y_offset+450, x_offset:x_offset+253] = video_frame
                    else:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            camera_width = 800
            camera_height = 450
            x_offset = 420
            y_offset = 185
            frame_rgb = cv2.resize(frame_rgb, (camera_width, camera_height))
            display_frame[y_offset:y_offset+camera_height, x_offset:x_offset+camera_width] = frame_rgb
            frame_surface = pygame.surfarray.make_surface(display_frame.swapaxes(0, 1))
            self.screen.blit(frame_surface, (0, 0))
            if self.current_exercise_index < len(self.exercises):
                exercise_text = self.font.render(f"Exercise: {self.exercises[self.current_exercise_index]}", True, (0, 151, 178))
            else:
                exercise_text = self.font.render("Exercise: Completed", True, (0, 151, 178))
            # label_text = self.font.render(f"Detected: {self.label}", True, (0, 0, 0))
            elapsed_time = (current_time - self.start_time) / 1000
            if elapsed_time >= 120 and self.current_exercise_index < len(self.exercises) - 1:
                if self.correct_count < self.required_correct_count:
                    self.start_time = current_time
                    # print(f"DEBUG: Time out, not enough points - Count: {self.correct_count}, Score: {self.score}, Total Score: {self.total_score}")
            elif elapsed_time >= 120 and self.current_exercise_index == len(self.exercises) - 1:
                if self.correct_count >= self.required_correct_count:
                    self.total_score += self.score
                    self._is_done = True
                    print(f"DEBUG: Level completed - Total Score: {self.total_score}")
            time_text = self.font.render(f"{int(120 - elapsed_time)}s", True, (0, 151, 178))
            score_text = self.font.render(f"{self.score}", True, (0, 151, 178))
            # Di chuyển Score và Time sang góc trên bên trái
            self.screen.blit(score_text, (100, 50))  # Góc trên bên trái
            self.screen.blit(time_text, (100, 100))   # Dịch xuống dưới score một chút
            # Di chuyển Exercise và Detected sang góc trên bên phải
            self.screen.blit(exercise_text, (self.screen_width - exercise_text.get_width() - 150, 100))  
            # self.screen.blit(label_text, (self.screen_width - label_text.get_width() - 50, 100))
            if self.show_plus_ten:
                self.screen.blit(self.plus_ten_image, (900, 200))  # Vị trí gần score
                if current_time - self.plus_ten_start_time >= 2000:  # Ẩn sau 2 giây
                    self.show_plus_ten = False     
            if self.show_congrat:
                self.screen.blit(self.congrat_image, (self.screen_width // 2 - 400, self.screen_height // 2 - 200))  # Giữa màn hình
                if current_time - self.congrat_start_time >= 2000:  # Ẩn sau 2 giây
                    self.show_congrat = False
                    if self.waiting_for_next_exercise:
                        self.correct_count = 0
                        self.score = 0
                        self.current_exercise_index += 1
                        self.start_time = current_time
                        self.waiting_for_next_exercise = False
                        self.sound_played = False  # Reset trạng thái âm thanh
                        elapsed_time = (current_time - self.start_time) / 1000
                        self.exercise_times.append(elapsed_time)
                        # print(f"DEBUG: Moved to next exercise - Index: {self.current_exercise_index}, Total Score: {self.total_score}, Exercise Time: {elapsed_time}s")

    def draw(self):
        pass

    def is_done(self):
        return self._is_done

    def get_score(self):
        return self.total_score

    def __del__(self):
        for cap in self.videos.values():
            cap.release()