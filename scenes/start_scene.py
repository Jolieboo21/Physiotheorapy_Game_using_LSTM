import pygame
from ui.button import Button
from settings import WIDTH, HEIGHT

class StartScene:
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/start_bg.png")
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.start_button = Button("assets/images/start_button.png", WIDTH // 2-150, HEIGHT // 2 + 100)
        self.next = False
        self.clicksound = pygame.mixer.Sound("assets/sounds/button-click.mp3")
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.is_clicked(pygame.mouse.get_pos()):
                self.next = True
                self.clicksound.play()

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.start_button.draw(self.screen)

    def is_done(self):
        return self.next