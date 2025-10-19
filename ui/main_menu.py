import pygame

from scenes.level import Level
from scenes.scene import Scene


class MainMenu(Scene):
    # start game button
    def __init__(self, screen: pygame.Surface, switch_scene_callback):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.start_button_rect = pygame.Rect(
            screen.get_width() // 2 - 150,
            screen.get_height() // 2 - 50,
            300,
            100,
        )
        self.switch_scene_callback = switch_scene_callback

    def setup(self):
        return super().setup()

    def render(self, dt: float):
        self.screen.fill((0, 0, 255))
        pygame.draw.rect(self.screen, (255, 255, 0), self.start_button_rect)
        text = self.font.render("Start Game", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        self.update(dt)

    def update(self, dt: float):
        if pygame.mouse.get_pressed()[0]:
            if self.start_button_rect.collidepoint(pygame.mouse.get_pos()):
                self.switch_scene_callback(Level(self.screen))
