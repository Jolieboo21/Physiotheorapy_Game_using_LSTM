import pygame
import os
import cv2
import numpy as np
from keras.models import load_model
import mediapipe as mp
from player import PlayerData
from scenes.level_1_scene import Level1Scene
from scenes.level_2_scene import Level2Scene
from scenes.level_3_scene import Level3Scene
from scenes.hand_exercise_scene import HandExerciseScene
from scenes.leg_exercise_scene import LegExerciseScene

pose = mp.solutions.pose.Pose()

class LoadingScene:
    def __init__(self, screen, next_scene_class, player_name, level, screen_width=1280, screen_height=720):
        self.screen = screen
        self.next_scene_class = next_scene_class
        self.player_name = player_name
        self.level = level  # 1, 2, 3, 4 (Hand), 5 (Leg)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.progress = 0
        self.loading_complete = False
        self.resources = {}
        self.cap = None
        self.model = None
        self.videos = {}
        self.bg = None
        self.plus_ten_image = None
        self.congrat_image = None
        self.score_sound = None
        self.next_ex_sound = None

    def load_resources(self):
        # Tải background
        self.bg = cv2.imread("assets/images/level1_bg.png")
        if self.bg is None:
            raise FileNotFoundError("Background image not found at: assets/images/level1_bg.png")
        self.bg = cv2.cvtColor(self.bg, cv2.COLOR_BGR2RGB)
        self.bg = cv2.resize(self.bg, (self.screen_width, self.screen_height))
        self.progress = 10

        # Tải model
        model_path = 'model/model_15.h5'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        try:
            self.model = load_model(model_path)
        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")
        self.progress = 30

        # Tải camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.screen_width)
        self.cap.set(4, self.screen_height)
        self.progress = 40

        # Tải 5 video phù hợp với level
        self.all_classes = ['knee_raise', 'forward_bend', 'arms_crossed', 'arms_legs_combined',
                           'leg_extension', 'arms_raised', 'arms_sideways', 'arms_front_chest',
                           'chest_exercise', 'arms_rotation']
        hand_classes = ['arms_raised', 'arms_sideways', 'arms_front_chest', 'chest_exercise', 'arms_rotation','forward_bend', 'arms_crossed']
        leg_classes = ['knee_raise', 'leg_extension', 'arms_legs_combined']

        if self.level == 4:  # Hand Exercise Level
            exercises = np.random.choice(hand_classes, 7, replace=False).tolist()
        elif self.level == 5:  # Leg Exercise Level
            exercises = np.random.choice(leg_classes, 3, replace=False).tolist()
        elif self.level == 3:  # Level 3
            exercises = np.random.choice(self.all_classes, 10, replace=False).tolist()  # Chọn 10 động tác
        else:  # Level 1, 2
            exercises = np.random.choice(self.all_classes, 5, replace=False).tolist()

        for exercise in exercises:
            for ext in ['.mov', '.mp4']:
                video_path = f"assets/videos/{exercise}{ext}"
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    self.videos[exercise] = cap
                    print(f"DEBUG: Loaded video for {exercise} at {video_path}")
                    break
            if exercise not in self.videos:
                raise FileNotFoundError(f"Video not found for {exercise} (.mov or .mp4)")
        self.progress = 60

        # Tải hình ảnh
        try:
            self.plus_ten_image = pygame.image.load("assets/images/plus.png").convert_alpha()
            self.congrat_image = pygame.image.load("assets/images/khen.png").convert_alpha()
            self.congrat_image = pygame.transform.scale(self.congrat_image, (800, 400))
        except FileNotFoundError:
            raise FileNotFoundError("Image files not found in assets/images/")
        except pygame.error as e:
            raise ValueError(f"Error loading images: {str(e)}")
        self.progress = 80

        # Tải âm thanh
        try:
            self.score_sound = pygame.mixer.Sound("assets/sounds/bell_3.mp3")
            self.score_sound.set_volume(0.2)
            self.next_ex_sound = pygame.mixer.Sound("assets/sounds/woosh.mp3")
        except FileNotFoundError:
            raise FileNotFoundError("Sound files not found in assets/sounds/")
        except pygame.error as e:
            raise ValueError(f"Error loading sounds: {str(e)}")
        self.progress = 100
        self.loading_complete = True

    def update(self):
        if not self.loading_complete:
            self.load_resources()
        return self.loading_complete

    def handle_event(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.loading_complete = True
            if self.cap:
                self.cap.release()
            for cap in self.videos.values():
                cap.release()

    def draw(self):
        self.screen.fill((0, 0, 0))
        loading_text = self.font.render("Loading...", True, (255, 255, 255))
        self.screen.blit(loading_text, (self.screen_width // 2 - loading_text.get_width() // 2, self.screen_height // 2 - 50))

        bar_width = 400
        bar_height = 30
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = self.screen_height // 2
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        current_width = (bar_width * self.progress) // 100
        pygame.draw.rect(self.screen, (0, 150, 0), (bar_x, bar_y, current_width, bar_height))

        percent_text = self.font.render(f"{self.progress}%", True, (255, 255, 255))
        self.screen.blit(percent_text, (self.screen_width // 2 - percent_text.get_width() // 2, bar_y + 40))

    def get_next_scene(self):
        if self.loading_complete:
            if self.next_scene_class == Level1Scene:
                return Level1Scene(self.screen, self.player_name, self.model, self.cap,
                                 {k: v for k, v in list(self.videos.items())[:3]}, self.bg,
                                 self.plus_ten_image, self.congrat_image, self.score_sound, self.next_ex_sound)
            elif self.next_scene_class == Level2Scene:
                return Level2Scene(self.screen, self.player_name, self.model, self.cap,
                                 {k: v for k, v in list(self.videos.items())[:5]}, self.bg,
                                 self.plus_ten_image, self.congrat_image, self.score_sound, self.next_ex_sound)
            elif self.next_scene_class == Level3Scene:
                return Level3Scene(self.screen, self.player_name, self.model, self.cap,
                                 self.videos, self.bg,
                                 self.plus_ten_image, self.congrat_image, self.score_sound, self.next_ex_sound)
            elif self.next_scene_class == HandExerciseScene:
                return HandExerciseScene(self.screen, self.player_name, self.model, self.cap,
                                      self.videos, self.bg,
                                      self.plus_ten_image, self.congrat_image, self.score_sound, self.next_ex_sound)
            elif self.next_scene_class == LegExerciseScene:
                return LegExerciseScene(self.screen, self.player_name, self.model, self.cap,
                                      self.videos, self.bg,
                                      self.plus_ten_image, self.congrat_image, self.score_sound, self.next_ex_sound)
        return None

    def is_done(self):
        return self.loading_complete

    def __del__(self):
        if self.cap:
            self.cap.release()
        for cap in self.videos.values():
            cap.release()