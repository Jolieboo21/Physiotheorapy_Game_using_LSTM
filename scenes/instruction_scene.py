import pygame
from ui.button import Button
from settings import WIDTH, HEIGHT
class InstructionScene:
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/instruction_bg.png")
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.next_button = Button("assets/images/play_bt.png",WIDTH // 2, HEIGHT // 2 + 270, width=200, height=100)
        self.next = False
        self.clicksound = pygame.mixer.Sound("assets/sounds/button-click.mp3")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.next_button.is_clicked(pygame.mouse.get_pos()):
                self.next = True
                self.clicksound.play()

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.next_button.draw(self.screen)

    def is_done(self):
        return self.next