import pygame
from ui.button import Button

exercise_mapping = {
    'knee_raise': 'Nâng đầu gối',
    'forward_bend': 'Cúi người về trước',
    'arms_crossed': 'Chéo tay',
    'arms_legs_combined': 'Kết hợp tay và chân',
    'leg_extension': 'Duỗi chân',
    'arms_raised': 'Nâng tay',
    'arms_sideways': 'Giơ tay ngang',
    'arms_front_chest': 'Tay trước ngực',
    'chest_exercise': 'Tập ngực',
    'arms_rotation': 'Xoay tay'
}

level_mapping = {
    'Hand Exercise': 'Tay nhanh',
    'Leg Exercise': 'Vừng bước',
    'Level 1': 'Khởi động',
    'Level 2': 'Linh hoạt',
    'Level 3': 'Thành thạo'
}

class ResultScene:
    def __init__(self, screen, player_data, all_players):
        self.screen = screen
        self.screen_width = 1280
        self.screen_height = 720
        self.font = pygame.font.Font("assets/fonts/K2D-light.ttf", 13)
        self.player_data = player_data
        self.stop_button = Button("assets/images/play_button.png", self.screen_width // 2 - 75 - 150, 600, width=150, height=75)
        self.next_button = Button("assets/images/play_button.png", self.screen_width // 2 + 75, 600, width=150, height=75)
        self._is_done = False
        self.next_scene = None
        self.all_players = all_players
        self.background = pygame.image.load("assets/images/result_bg.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._is_done = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.stop_button.is_clicked(mouse_pos):
                self._is_done = True
                self.next_scene = None
            elif self.next_button.is_clicked(mouse_pos):
                self._is_done = True
                self.next_scene = "LevelSelectScene"

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        name_text = self.font.render(f"Tên người tập: {self.player_data.name}", True, (0, 0, 0))
        total_score_text = self.font.render(f"Điểm tổng: {self.player_data.total_score}", True, (0, 0, 0))
        total_time_text = self.font.render(f"Thời gian tổng: {self.player_data.total_time:.2f}s", True, (0, 0, 0))
        level_text = self.font.render(f"Cấp độ: {level_mapping.get(self.player_data.level, self.player_data.level)}", True, (0, 0, 0))
        self.screen.blit(name_text, (50, 425))
        self.screen.blit(total_score_text, (50, 450))
        self.screen.blit(total_time_text, (50, 475))
        self.screen.blit(level_text, (50, 500))

        chart_x, chart_y, chart_width, chart_height = 70, 50, 1000, 300
        num_exercises = len(self.player_data.exercise_names)
        bar_width = chart_width / (num_exercises * 2 + 1) if num_exercises > 0 else 10
        max_score = max(self.player_data.exercise_scores) if self.player_data.exercise_scores else 1
        max_time = max(self.player_data.exercise_times) if self.player_data.exercise_times else 1

        for i, (name, score, time) in enumerate(zip(self.player_data.exercise_names, self.player_data.exercise_scores, self.player_data.exercise_times)):
            bar_height_score = (score / max_score) * chart_height
            bar_x_score = chart_x + (chart_width - (num_exercises * 2 * bar_width)) / 2 + i * 2 * bar_width
            pygame.draw.rect(self.screen, (255, 165, 0), (bar_x_score, chart_y + chart_height - bar_height_score, bar_width - 5, bar_height_score))
            self.screen.blit(self.font.render(f"{score}", True, (0, 0, 0)), (bar_x_score, chart_y + chart_height - bar_height_score - 20))

            bar_height_time = (time / max_time) * chart_height
            bar_x_time = bar_x_score + bar_width
            pygame.draw.rect(self.screen, (255, 200, 100), (bar_x_time, chart_y + chart_height - bar_height_time, bar_width - 5, bar_height_time))
            self.screen.blit(self.font.render(f"{time:.2f}", True, (0, 0, 0)), (bar_x_time, chart_y + chart_height - bar_height_time - 20))

            name_text = self.font.render(name, True, (0, 0, 0))
            self.screen.blit(name_text, (bar_x_score + bar_width / 2 - name_text.get_width() / 2, chart_y + chart_height + 10))

        legend_x = chart_x + chart_width + 20
        self.screen.blit(self.font.render("Điểm", True, (255, 165, 0)), (legend_x, chart_y))
        self.screen.blit(self.font.render("Thời gian", True, (255, 200, 100)), (legend_x, chart_y + 40))

        if self.player_data.exercise_scores and self.player_data.exercise_times:
            best_index = max(range(len(self.player_data.exercise_scores)), key=lambda i: (self.player_data.exercise_scores[i], -self.player_data.exercise_times[i]))
            worst_index = min(range(len(self.player_data.exercise_scores)), key=lambda i: (self.player_data.exercise_scores[i], self.player_data.exercise_times[i]))

            best_text = self.font.render(f"Động tác tốt nhất: {self.player_data.exercise_names[best_index]} (Điểm: {self.player_data.exercise_scores[best_index]}, Thời gian: {self.player_data.exercise_times[best_index]:.2f}s)", True, (0, 255, 0))
            worst_text = self.font.render(f"Động tác cần cải thiện: {self.player_data.exercise_names[worst_index]} (Điểm: {self.player_data.exercise_scores[worst_index]}, Thời gian: {self.player_data.exercise_times[worst_index]:.2f}s)", True, (255, 0, 0))
            self.screen.blit(best_text, (50, 525))
            self.screen.blit(worst_text, (50, 550))

        # Bảng xếp hạng 3 dòng
        if self.player_data.level and self.all_players:
            current_level_players = [p for p in self.all_players if p.level == self.player_data.level]
            if current_level_players:
                current_level_players.sort(key=lambda x: (x.total_score, -x.total_time), reverse=True)
                player_index = next((i for i, p in enumerate(current_level_players) if p.name == self.player_data.name), None)

                table_x = 650
                table_y = 480
                cell_widths = [60, 200, 100, 120]
                cell_height = 30
                line_spacing = 10

                display_rows = []
                rank1 = current_level_players[0]
                display_rows.append(("", rank1.name, rank1.total_score, f"{rank1.total_time:.2f}s"))

                if player_index is not None and player_index > 0:
                    above_player = current_level_players[player_index - 1]
                    display_rows.append((f"{player_index}", above_player.name, above_player.total_score, f"{above_player.total_time:.2f}s"))
                else:
                    display_rows.append(("-", "Không có người chơi đứng trên", "", ""))

                current_rank = player_index + 1 if player_index is not None else len(current_level_players) + 1
                display_rows.append((f"{current_rank}", self.player_data.name, self.player_data.total_score, f"{self.player_data.total_time:.2f}s"))

                for row_idx, row_data in enumerate(display_rows):
                    x = table_x
                    y = table_y + row_idx * (cell_height + line_spacing)
                    for col_idx, cell in enumerate(row_data):
                        col_width = cell_widths[col_idx]
                        color = (0, 0, 200) if row_idx == 2 else (0, 0, 0)
                        cell_surface = self.font.render(str(cell), True, color)
                        text_rect = cell_surface.get_rect(center=(x + col_width // 2, y + cell_height // 2))
                        self.screen.blit(cell_surface, text_rect)
                        x += col_width

        self.stop_button.draw(self.screen)
        self.next_button.draw(self.screen)

    def is_done(self):
        return self._is_done

    def get_next_scene(self):
        return self.next_scene
