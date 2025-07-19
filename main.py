import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from scenes.start_scene import StartScene
from scenes.name_input_scene import NameInputScene
from scenes.introduction_scene import IntroductionScene
from scenes.instruction_scene import InstructionScene
from scenes.level_select_scene import LevelSelectScene
from scenes.level_1_scene import Level1Scene
from scenes.level_2_scene import Level2Scene
from scenes.level_3_scene import Level3Scene
from save_manager import save_score
from player import PlayerData

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Khởi tạo các scene
scenes = [
    StartScene(screen),
    NameInputScene(screen),
    IntroductionScene(screen),
    InstructionScene(screen),
    LevelSelectScene(screen)
]
current_index = 0
player = None  # Sẽ khởi tạo sau

running = True
while running:
    current_scene = scenes[current_index]

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        current_scene.handle_event(event)

    current_scene.update()
    current_scene.draw()
    pygame.display.flip()
    clock.tick(FPS)

    if current_scene.is_done():
        if isinstance(current_scene, NameInputScene):
            player = current_scene.get_player()
        elif isinstance(current_scene, (Level1Scene, Level2Scene, Level3Scene)):
            if player is None:  # Khởi tạo player nếu chưa có
                player = PlayerData("Default", 0)
            player.score += current_scene.get_score()  # Cộng dồn điểm từ scene
            save_score(player)  # Lưu điểm sau khi hoàn thành
        elif isinstance(current_scene, LevelSelectScene):
            if current_scene.next_scene == 0:
                scenes.append(Level1Scene(screen))
            elif current_scene.next_scene == 1:
                scenes.append(Level2Scene(screen))
            elif current_scene.next_scene == 2:
                scenes.append(Level3Scene(screen))
        current_index += 1
        if current_index >= len(scenes):
            running = False

pygame.quit()
sys.exit()