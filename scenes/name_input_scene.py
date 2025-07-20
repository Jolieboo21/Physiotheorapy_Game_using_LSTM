import pygame
from player import PlayerData
from settings import WIDTH, HEIGHT, WHITE, BLACK

class NameInputScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("K2D", 48)
        self.name = ""
        self.done = False
        self.bg = pygame.image.load("assets/images/input_name_bg.png")
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))

        # Thiết lập khung cố định
        self.box_width = 500
        self.box_height = 80
        self.box_rect = pygame.Rect(
            WIDTH // 2 - self.box_width // 2,
            HEIGHT // 2 - 70 - self.box_height // 2+50,
            self.box_width,
            self.box_height
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.done = True
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            else:
                if len(self.name) < 12 and event.unicode.isprintable():
                    self.name += event.unicode

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        # Vẽ khung input có bo góc
        pygame.draw.rect(self.screen, WHITE, self.box_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, self.box_rect, width=2, border_radius=15)

        # Hiển thị con nháy nhấp nháy
        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
        display_name = self.name + ('|' if cursor_visible else '')

        # Vẽ text nằm giữa trong khung
        text_surface = self.font.render(display_name, True, BLACK)
        text_rect = text_surface.get_rect(center=self.box_rect.center)
        self.screen.blit(text_surface, text_rect)

    def is_done(self):
        return self.done

    def get_player(self):
        return PlayerData(self.name, 0)  # Truyền score mặc định là 0
