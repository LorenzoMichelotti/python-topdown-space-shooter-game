import pygame

from entities.static import Static


class DamageNumber(Static):
    def __init__(self, screen, pos, damage_amount):
        super().__init__(screen, pos)
        self.damage_amount = damage_amount
        self.lifetime = 1.0  # seconds
        self.elapsed_time = 0.0
        self.velocity = pygame.Vector2(0, -50)  # Move upwards
        self.layer = 10
        self.height = 5

    def move(self, delta_time):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.lifetime:
            self.entity_manager.destroy(self)
            return

        # Update position
        self.pos += self.velocity * delta_time

    def draw(self):
        font = pygame.font.SysFont("Arial", 32, True)
        text_surface = font.render(str(self.damage_amount), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.screen.blit(text_surface, text_rect)

    def draw_shadow(self):
        # Shadows for damage numbers can be simple offsets
        font = pygame.font.SysFont("Arial", 32, True)
        text_surface = font.render(str(self.damage_amount), True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            center=(int(self.pos.x), int(self.pos.y + self.height))
        )
        self.screen.blit(text_surface, text_rect)
