import pygame
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import os
import threading
from keras.models import load_model

pose = mp.solutions.pose.Pose()
mpDraw = mp.solutions.drawing_utils

class Level1Scene:
    def __init__(self, screen):
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
        self.score = 0
        self.current_exercise_index = 0
        self.required_score = 100
        self._is_done = False
        self.font = pygame.font.Font(None, 36)
        # Khởi tạo background
        self.bg = cv2.imread("assets/images/level1_bg.png")
        if self.bg is None:
            raise FileNotFoundError("Background image not found at: assets/images/level1_bg.png")
        self.bg = cv2.cvtColor(self.bg, cv2.COLOR_BGR2RGB)  # Chuyển sang RGB
        self.bg = cv2.resize(self.bg, (self.screen_width, self.screen_height))
        # Khởi tạo video cho từng exercise
        self.videos = {}
        for exercise in self.exercises:
            for ext in ['.mov', '.mp4']:
                video_path = f"assets/videos/{exercise}{ext}"
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    self.videos[exercise] = cap
                    break
            if exercise not in self.videos:
                raise FileNotFoundError(f"Video not found for {exercise} (.mov or .mp4)")
        self.start_time = pygame.time.get_ticks()  # Thời gian bắt đầu

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
            if confidence > 0.95 and self.classes[predicted_label_index] == self.exercises[self.current_exercise_index]:
                self.label = self.classes[predicted_label_index]
                self.score += 10
                if self.score >= self.required_score:
                    self.score = 0
                    self.current_exercise_index += 1
                    if self.current_exercise_index >= len(self.exercises):
                        self._is_done = True
            else:
                self.label = "neutral"
            self.lm_list = []

    def draw_landmark_on_image(self, results, frame):
        mpDraw.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
        h, w, c = frame.shape
        bbox = []
        if results.pose_landmarks:
            for id, lm in enumerate(results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                bbox.append([cx, cy])
            x_min, y_min = np.min(bbox, axis=0)
            x_max, y_max = np.max(bbox, axis=0)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        return frame

    def handle_event(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._is_done = True

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            # Debug định dạng frame camera
            print("Camera frame shape:", frame.shape, "dtype:", frame.dtype)
            # Thử chuyển đổi từ YUV sang RGB nếu cần
            if frame.shape[2] == 3:  # Nếu là 3 kênh (BGR)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:  # Giả sử YUV (thường là YUYV hoặc NV12)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_I420)  # Thử I420, điều chỉnh nếu cần
            results = pose.process(frame_rgb)
            if results.pose_landmarks:
                lm = self.make_landmark_timestep(results)
                self.lm_list.append(lm)
                if len(self.lm_list) == 7:
                    detect_thread = threading.Thread(target=self.detect)
                    detect_thread.start()
                    detect_thread.join()
                    self.lm_list = []
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)  # Quay lại BGR để vẽ landmark
            frame = self.draw_landmark_on_image(results, frame)
            # Chuẩn bị background để vẽ
            display_frame = self.bg.copy()
            # Hiển thị video của động tác hiện tại ở góc dưới bên trái
            h, w = display_frame.shape[:2]
            video_width = 253 # 1/4 chiều rộng
            video_height = 450 # 1/2 chiều cao
            if self.current_exercise_index < len(self.exercises):
                current_exercise = self.exercises[self.current_exercise_index]
                cap = self.videos[current_exercise]
                ret_video, video_frame = cap.read()
                if ret_video:
                    video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)  # Chuyển sang RGB
                    video_frame = cv2.resize(video_frame, (video_width, video_height))
                    x_offset = 50  
                    y_offset = 185
                    display_frame[y_offset:y_offset+video_height, x_offset:x_offset+video_width] = video_frame
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            # Hiển thị camera ở góc dưới bên phải
            camera_width = 800 
            camera_height = 450
            x_offset = 420 
            y_offset = 185
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Chuyển camera sang RGB
            frame_rgb = cv2.resize(frame_rgb, (camera_width, camera_height))
            display_frame[y_offset:y_offset+camera_height, x_offset:x_offset+camera_width] = frame_rgb
            # Chuyển sang pygame surface với swapaxes để điều chỉnh định hướng
            frame_surface = pygame.surfarray.make_surface(display_frame.swapaxes(0, 1))
            self.screen.blit(frame_surface, (0, 0))
            # Vẽ thông tin bằng Pygame với màu đen
            if self.current_exercise_index < len(self.exercises):
                exercise_text = self.font.render(f"Exercise: {self.exercises[self.current_exercise_index]}", True, (0, 0, 0))
            else:
                exercise_text = self.font.render("Exercise: Completed", True, (0, 0, 0))
            label_text = self.font.render(f"Detected: {self.label}", True, (0, 0, 0))
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.start_time) / 1000
            if elapsed_time >= 120:
                self.score = 0
                self.current_exercise_index += 1
                self.start_time = current_time
                if self.current_exercise_index >= len(self.exercises):
                    self._is_done = True
            time_text = self.font.render(f"Time: {int(120 - elapsed_time)}s", True, (0, 0, 0))
            score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
            self.screen.blit(exercise_text, (20, 20))
            self.screen.blit(label_text, (20, 60))
            self.screen.blit(time_text, (20, 100))
            self.screen.blit(score_text, (20, 140))

    def draw(self):
        pass  # Không cần draw riêng vì đã xử lý trong update

    def is_done(self):
        return self._is_done

    def get_score(self):
        return self.score

    def __del__(self):
        for cap in self.videos.values():
            cap.release()