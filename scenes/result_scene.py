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

# Ánh xạ tên level sang tiếng Việt
level_mapping = {
    'Hand Exercise': 'Tay nhanh',
    'Leg Exercise': 'Vững bước',
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
        self.all_players = all_players  # Danh sách tất cả người chơi từ PlayerData

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
        self.screen.fill((255, 255, 255))

        # Hiển thị thông tin tổng hợp
        name_text = self.font.render(f"Tên người tập: {self.player_data.name}", True, (0, 0, 0))
        total_score_text = self.font.render(f"Điểm tổng: {self.player_data.total_score}", True, (0, 0, 0))
        total_time_text = self.font.render(f"Thời gian tổng: {self.player_data.total_time:.2f}s", True, (0, 0, 0))
        level_text = self.font.render(f"Cấp độ: {level_mapping.get(self.player_data.level, self.player_data.level)}", True, (0, 0, 0))
        self.screen.blit(name_text, (50, 50))
        self.screen.blit(total_score_text, (50, 100))
        self.screen.blit(total_time_text, (50, 150))
        self.screen.blit(level_text, (50, 200))

        # Vẽ biểu đồ cột
        chart_x = 700
        chart_y = 20
        chart_width = 350
        chart_height = 250
        num_exercises = len(self.player_data.exercise_names)
        bar_width = chart_width / (num_exercises * 2 + 1) if num_exercises > 0 else 10
        max_score = max(self.player_data.exercise_scores) if self.player_data.exercise_scores else 1
        max_time = max(self.player_data.exercise_times) if self.player_data.exercise_times else 1

        for i, (name, score, time) in enumerate(zip(self.player_data.exercise_names, self.player_data.exercise_scores, self.player_data.exercise_times)):
            # Cột điểm (xanh lá)
            bar_height_score = (score / max_score) * chart_height
            bar_x_score = chart_x + (chart_width - (num_exercises * 2 * bar_width)) / 2 + i * 2 * bar_width
            bar_rect_score = pygame.Rect(bar_x_score, chart_y + chart_height - bar_height_score, bar_width - 5, bar_height_score)
            pygame.draw.rect(self.screen, (0, 255, 0), bar_rect_score)
            score_text = self.font.render(f"{score}", True, (0, 0, 0))
            self.screen.blit(score_text, (bar_x_score, chart_y + chart_height - bar_height_score - 20))

            # Cột thời gian (vàng)
            bar_height_time = (time / max_time) * chart_height
            bar_x_time = bar_x_score + bar_width
            bar_rect_time = pygame.Rect(bar_x_time, chart_y + chart_height - bar_height_time, bar_width - 5, bar_height_time)
            pygame.draw.rect(self.screen, (255, 255, 0), bar_rect_time)
            time_text = self.font.render(f"{time:.2f}", True, (0, 0, 0))
            self.screen.blit(time_text, (bar_x_time, chart_y + chart_height - bar_height_time - 20))

            # Nhãn tên bài tập
            name_text = self.font.render(name, True, (0, 0, 0))
            self.screen.blit(name_text, (bar_x_score + bar_width / 2 - name_text.get_width() / 2, chart_y + chart_height + 10))

        # Chú thích
        legend_x = chart_x + chart_width + 20
        legend_y = chart_y
        score_legend = self.font.render("Điểm (Xanh lá)", True, (0, 255, 0))
        time_legend = self.font.render("Thời gian (Vàng)", True, (255, 255, 0))
        self.screen.blit(score_legend, (legend_x, legend_y))
        self.screen.blit(time_legend, (legend_x, legend_y + 40))

        # Phân tích động tác tốt nhất và cần cải thiện
        if self.player_data.exercise_scores and self.player_data.exercise_times:
            indices = range(len(self.player_data.exercise_scores))
            scores = self.player_data.exercise_scores
            times = self.player_data.exercise_times

            # Động tác tốt nhất (điểm cao nhất, thời gian thấp nhất)
            best_index = max(indices, key=lambda i: (scores[i], -times[i]))
            best_text = self.font.render(f"Động tác tốt nhất: {self.player_data.exercise_names[best_index]} (Điểm: {scores[best_index]}, Thời gian: {times[best_index]:.2f}s)", True, (0, 255, 0))
            self.screen.blit(best_text, (50, 500))

            # Động tác cần cải thiện (điểm thấp nhất, thời gian cao nhất)
            worst_index = min(indices, key=lambda i: (scores[i], times[i]))
            worst_text = self.font.render(f"Động tác cần cải thiện: {self.player_data.exercise_names[worst_index]} (Điểm: {scores[worst_index]}, Thời gian: {times[worst_index]:.2f}s)", True, (255, 0, 0))
            self.screen.blit(worst_text, (50, 550))

        # Bảng xếp hạng
        if self.player_data.level and self.all_players:
            # Lọc bảng xếp hạng theo level hiện tại
            current_level_players = [p for p in self.all_players if p.level == self.player_data.level]
            if current_level_players:
                # Sắp xếp theo tổng điểm (giảm dần) và tổng thời gian (tăng dần)
                current_level_players.sort(key=lambda x: (x.total_score, -x.total_time), reverse=True)
                player_index = next((i for i, p in enumerate(current_level_players) if p.name == self.player_data.name), None)

                # Hiển thị thông tin
                rank1 = current_level_players[0]
                rank1_text = self.font.render(f"Hạng 1: {rank1.name} (Điểm: {rank1.total_score}, Thời gian: {rank1.total_time:.2f}s)", True, (0, 0, 0))
                self.screen.blit(rank1_text, (700, 500))

                if player_index is not None and player_index > 0:
                    above_player = current_level_players[player_index - 1]
                    above_text = self.font.render(f"Hạng {player_index}: {above_player.name} (Điểm: {above_player.total_score}, Thời gian: {above_player.total_time:.2f}s)", True, (0, 0, 0))
                    self.screen.blit(above_text, (700, 550))
                else:
                    above_text = self.font.render("Không có người chơi đứng trên", True, (0, 0, 0))
                    self.screen.blit(above_text, (700, 550))

                current_rank = player_index + 1 if player_index is not None else len(current_level_players) + 1
                current_text = self.font.render(f"Hạng của bạn: {current_rank} (Điểm: {self.player_data.total_score}, Thời gian: {self.player_data.total_time:.2f}s)", True, (0, 0, 0))
                self.screen.blit(current_text, (700, 600))

        # Vẽ nút
        self.stop_button.draw(self.screen)
        self.next_button.draw(self.screen)

    def is_done(self):
        return self._is_done

    def get_next_scene(self):
        return self.next_scene