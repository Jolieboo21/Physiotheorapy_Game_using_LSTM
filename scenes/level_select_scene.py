import pygame
from ui.button import Button
from settings import WIDTH, HEIGHT

class LevelSelectScene:
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/level_bg.png")
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.level1_button = Button("assets/images/level1_button.png", WIDTH // 2 - 390, 590, width=150, height=75)
        self.level2_button = Button("assets/images/level2_button.png", WIDTH // 2, 590, width=150, height=75)
        self.level3_button = Button("assets/images/level3_button.png", WIDTH // 2 + 390, 590, width=150, height=75)
        self.hand_exercise_button = Button("assets/images/level_hand_button.png", WIDTH // 2 - 195, 330, width=150, height=75)
        self.leg_exercise_button = Button("assets/images/level_leg_button.png", WIDTH // 2 + 195, 330, width=150, height=75)
        self._is_done = False
        self.clicksound = pygame.mixer.Sound("assets/sounds/button-click.mp3")
        self.next_scene = 0  # Giá trị mặc định, 0 nghĩa là chưa chọn

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._is_done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._is_done = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.level1_button.is_clicked(mouse_pos):
                self.next_scene = 1  # Level 1
                self.clicksound.play()
                self._is_done = True
                print(f"DEBUG: Selected Level 1")
            elif self.level2_button.is_clicked(mouse_pos):
                self.next_scene = 2  # Level 2
                self.clicksound.play()
                self._is_done = True
                print(f"DEBUG: Selected Level 2")
            elif self.level3_button.is_clicked(mouse_pos):
                self.next_scene = 3  # Level 3
                self.clicksound.play()
                self._is_done = True
                print(f"DEBUG: Selected Level 3")
            elif self.hand_exercise_button.is_clicked(mouse_pos):
                self.next_scene = 4  # Hand Exercise Level
                self.clicksound.play()
                self._is_done = True
                print(f"DEBUG: Selected Hand Exercise Level")
            elif self.leg_exercise_button.is_clicked(mouse_pos):
                self.next_scene = 5  # Leg Exercise Level
                self.clicksound.play()
                self._is_done = True
                print(f"DEBUG: Selected Leg Exercise Level")

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.level1_button.draw(self.screen)
        self.level2_button.draw(self.screen)
        self.level3_button.draw(self.screen)
        self.hand_exercise_button.draw(self.screen)
        self.leg_exercise_button.draw(self.screen)

    def is_done(self):
        return self._is_done

    def get_level_choice(self):  # Trả về lựa chọn level
        return self.next_scene