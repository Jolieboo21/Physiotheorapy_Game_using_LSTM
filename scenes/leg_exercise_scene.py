import pygame
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
from save_manager import save_score
from scenes.level_1_scene import Level1Scene, exercise_mapping  # Nhập exercise_mapping

class LegExerciseScene(Level1Scene):
    def __init__(self, screen, player_name, model, cap, videos, bg, plus_ten_image, congrat_image, score_sound, next_ex_sound):
        super().__init__(screen, player_name, model, cap, videos, bg, plus_ten_image, congrat_image, score_sound, next_ex_sound)
        self.exercise_keys = list(videos.keys())  # Sử dụng tất cả 5 khóa tiếng Anh cho tìm video
        self.exercises = [exercise_mapping[key] for key in self.exercise_keys]  # Ánh xạ sang tiếng Việt cho hiển thị
        self.exercise_names = self.exercises.copy()  # Tên tiếng Việt để lưu
        self.level = "Leg Exercise"  # Tên level cụ thể
        print(f"DEBUG: LegExerciseScene exercises: {self.exercises}, exercise_keys: {self.exercise_keys}, videos keys: {list(videos.keys())}")