import pygame
import json
from datetime import datetime
from scenes.start_scene import StartScene
from scenes.name_input_scene import NameInputScene
from scenes.introduction_scene import IntroductionScene
from scenes.instruction_scene import InstructionScene
from scenes.level_select_scene import LevelSelectScene
from scenes.loading_scene import LoadingScene
from scenes.level_1_scene import Level1Scene
from scenes.level_2_scene import Level2Scene
from scenes.level_3_scene import Level3Scene
from scenes.hand_exercise_scene import HandExerciseScene
from scenes.leg_exercise_scene import LegExerciseScene
from scenes.result_scene import ResultScene
from player import PlayerData
from save_manager import save_score, load_scores  # Sử dụng load_scores

# Khởi tạo Pygame và mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("ARIA Game")
clock = pygame.time.Clock()

# Tải và phát nhạc nền
music_path = "assets/sounds/bg_music.mp3"
try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except FileNotFoundError:
    print(f"DEBUG: Music file not found at {music_path}")
except pygame.error as e:
    print(f"DEBUG: Error loading music: {str(e)}")

# Đọc dữ liệu từ scores.json
all_players = load_scores()  # Sử dụng load_scores từ save_manager

# Khởi tạo danh sách scene ban đầu
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
            print(f"DEBUG: Created PlayerData - Name: {player_name}, Score: {player.total_score}")
            current_scene_index += 1
        elif isinstance(scenes[current_scene_index], LevelSelectScene):
            level_choice = scenes[current_scene_index].get_level_choice()
            if level_choice in [1, 2, 3, 4, 5]:
                if level_choice == 1:
                    scenes.append(LoadingScene(screen, Level1Scene, player_name, 1))
                elif level_choice == 2:
                    scenes.append(LoadingScene(screen, Level2Scene, player_name, 2))
                elif level_choice == 3:
                    scenes.append(LoadingScene(screen, Level3Scene, player_name, 3))
                elif level_choice == 4:
                    scenes.append(LoadingScene(screen, HandExerciseScene, player_name, 4))
                elif level_choice == 5:
                    scenes.append(LoadingScene(screen, LegExerciseScene, player_name, 5))
                current_scene_index += 1
        elif isinstance(scenes[current_scene_index], LoadingScene):
            next_scene = scenes[current_scene_index].get_next_scene()
            if next_scene:
                scenes.append(next_scene)
                current_scene_index += 1
        elif isinstance(scenes[current_scene_index], (Level1Scene, Level2Scene, Level3Scene, HandExerciseScene, LegExerciseScene)):
            scene = scenes[current_scene_index]
            level = getattr(scene, 'level', "Level 1" if isinstance(scene, Level1Scene) else 
                           "Level 2" if isinstance(scene, Level2Scene) else 
                           "Level 3" if isinstance(scene, Level3Scene) else 
                           "Hand Exercise" if isinstance(scene, HandExerciseScene) else 
                           "Leg Exercise")
            player = PlayerData(
                player_name,
                scene.get_score(),
                round(sum(scene.exercise_times), 2),
                level,
                exercise_names=getattr(scene, 'exercise_names', []),
                exercise_scores=scene.exercise_scores,
                exercise_times=scene.exercise_times
            )
            print(f"DEBUG: Auto-saving after level - Scene type: {type(scene).__name__}, Level from attr: {getattr(scene, 'level', 'N/A')}, Calculated Level: {level}, Player: {player.name}, Score: {player.total_score}, Time: {player.total_time}, Saved Level: {player.level}")
            save_score(player)
            # Cập nhật all_players sau khi lưu
            all_players = load_scores()  # Tải lại để đảm bảo dữ liệu mới nhất
            scenes.append(ResultScene(screen, player, all_players))
            current_scene_index += 1
        elif isinstance(scenes[current_scene_index], ResultScene):
            next_scene = scenes[current_scene_index].get_next_scene()
            if next_scene == "LevelSelectScene":
                scenes.append(LevelSelectScene(screen))
                current_scene_index += 1
            elif next_scene is None:  # Thoát game
                running = False
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