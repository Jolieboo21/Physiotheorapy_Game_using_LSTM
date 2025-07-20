import pygame
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
from save_manager import save_score
from scenes.level_1_scene import Level1Scene

class Level2Scene(Level1Scene):
    def __init__(self, screen, player_name):
        super().__init__(screen, player_name)  # Truyền player_name
        self.exercises = np.random.choice(self.classes, 5, replace=False).tolist()  # 5 động tác
        self.level = "Level 2"  # Định nghĩa level cụ thể
        # Tải lại video cho các bài tập mới
        self.videos = {}
        for exercise in self.exercises:
            video_found = False
            for ext in ['.mov', '.mp4']:
                video_path = f"assets/videos/{exercise}{ext}"
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    self.videos[exercise] = cap
                    video_found = True
                    print(f"DEBUG: Loaded video for {exercise} at {video_path}")
                    break
            if not video_found:
                raise FileNotFoundError(f"Video not found for {exercise} (.mov or .mp4)")