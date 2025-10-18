import pygame

from entities.static import Static


class Cursor(Static):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.height = 10
        self.layer = 4
        self.size = 80
        self.original_sprite = pygame.image.load(
            "assets/sprites/cursor_sprite.png"
        ).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.original_sprite, (self.size, self.size)
        )

    def draw_shadow(self):
        # Scale shadow with cursor
        shadow_sprite = pygame.transform.scale(
            self.original_sprite, (self.size, self.size)
        )
        shadow_rect = shadow_sprite.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )

        # Create a darkened version for shadow
        shadow_surface = shadow_sprite.copy()
        shadow_surface.fill((0, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)

        self.screen.blit(shadow_surface, shadow_rect)

    def draw(self):
        rect = self.sprite.get_rect(center=(self.pos.x, self.pos.y))
        self.screen.blit(self.sprite, rect)

    def move(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        self.pos = pygame.Vector2(mouse_pos[0], mouse_pos[1])

        if pygame.mouse.get_pressed()[0]:
            self.size = 70
        else:
            self.size = 80

        self.sprite = pygame.transform.scale(
            self.original_sprite, (self.size, self.size)
        )
