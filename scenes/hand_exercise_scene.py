import pygame
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
from save_manager import save_score
from scenes.level_1_scene import Level1Scene

class HandExerciseScene(Level1Scene):
    def __init__(self, screen, player_name, model, cap, videos, bg, plus_ten_image, congrat_image, score_sound, next_ex_sound):
        super().__init__(screen, player_name, model, cap, videos, bg, plus_ten_image, congrat_image, score_sound, next_ex_sound)
        self.exercises = list(videos.keys())  # Sử dụng tất cả 5 video
        self.level = "Hand Exercise"
        print(f"DEBUG: HandExerciseScene exercises: {self.exercises}, videos keys: {list(videos.keys())}")