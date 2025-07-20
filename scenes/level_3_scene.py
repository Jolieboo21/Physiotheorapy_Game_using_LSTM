import pygame
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
from save_manager import save_score
from scenes.level_1_scene import Level1Scene

class Level3Scene(Level1Scene):
    def __init__(self, screen, player_name):
        super().__init__(screen, player_name)  # Truyền player_name
        self.exercises = np.random.choice(self.classes, 10, replace=False).tolist()  # 10 động tác
        self.level = "Level 3"  # Định nghĩa level cụ thể