import pygame
from scenes.start_scene import StartScene
from scenes.name_input_scene import NameInputScene
from scenes.introduction_scene import IntroductionScene
from scenes.instruction_scene import InstructionScene
from scenes.level_select_scene import LevelSelectScene
from scenes.level_1_scene import Level1Scene
from scenes.level_2_scene import Level2Scene
from scenes.level_3_scene import Level3Scene
from player import PlayerData
from save_manager import save_score

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)  # Khởi tạo mixer
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("ARIA Game")
clock = pygame.time.Clock()

# Tải và phát nhạc nền
music_path = "assets/sounds/bg_music.mp3"  # Thay bằng tên file thực tế
try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Phát lặp lại vô hạn (-1)
except FileNotFoundError:
    print(f"DEBUG: Music file not found at {music_path}")
except pygame.error as e:
    print(f"DEBUG: Error loading music: {str(e)}")

scenes = [
    StartScene(screen),
    NameInputScene(screen),
    IntroductionScene(screen),
    InstructionScene(screen),
    LevelSelectScene(screen)
]

current_scene_index = 0
player_name = None
player = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scenes[current_scene_index].handle_event(event)

    if scenes[current_scene_index].is_done():
        if isinstance(scenes[current_scene_index], NameInputScene):
            player = scenes[current_scene_index].get_player()
            player_name = player.name
            print(f"DEBUG: Created PlayerData - Name: {player_name}, Score: {player.score}")
            current_scene_index += 1
        elif isinstance(scenes[current_scene_index], LevelSelectScene):
            level_choice = scenes[current_scene_index].get_level_choice()
            if level_choice == 1:
                scenes.append(Level1Scene(screen, player_name))
            elif level_choice == 2:
                scenes.append(Level2Scene(screen, player_name))
            elif level_choice == 3:
                scenes.append(Level3Scene(screen, player_name))
            current_scene_index += 1
        elif isinstance(scenes[current_scene_index], (Level1Scene, Level2Scene, Level3Scene)):
            scene = scenes[current_scene_index]
            level = getattr(scene, 'level', "Level 1" if isinstance(scene, Level1Scene) else "Level 2" if isinstance(scene, Level2Scene) else "Level 3")
            player = PlayerData(
                player_name,
                scene.get_score(),
                round(sum(scene.exercise_times), 2),
                level
            )
            print(f"DEBUG: Auto-saving after level - Scene type: {type(scene).__name__}, Level from attr: {getattr(scene, 'level', 'N/A')}, Calculated Level: {level}, Player: {player.name}, Score: {player.score}, Time: {player.total_time}, Saved Level: {player.level}")
            save_score(player)
            current_scene_index += 1
        else:
            current_scene_index += 1

    if 0 <= current_scene_index < len(scenes):
        scenes[current_scene_index].update()
        scenes[current_scene_index].draw()
    else:
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()