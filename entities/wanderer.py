import pygame
import random
from entities.base_enemy import BaseEnemy


class Wanderer(BaseEnemy):
    """Enemy variant that wanders randomly instead of chasing the player"""

    def __init__(self, screen: pygame.Surface, initial_pos: pygame.Vector2):
        super().__init__(screen, initial_pos)
        self.max_speed = 100  # Slower than regular enemies
        self.acceleration = 800

        # Wandering behavior
        self.wander_timer = 0
        self.wander_interval = random.uniform(
            1.0, 3.0
        )  # Change direction every 1-3 seconds
        self.wander_direction = self._get_random_direction()

    def _get_random_direction(self):
        angle = random.uniform(0, 360)
        rad = pygame.math.Vector2(1, 0).rotate(angle)
        return rad.normalize()

    def draw(self):
        self.draw_sprite_with_color(color_tint=(255, 255, 100))

    def calculate_acceleration(self, dt: float) -> pygame.Vector2:
        # Don't wander while growing
        if self.is_growing:
            return pygame.Vector2(0, 0)

        # Update wander timer
        self.wander_timer += dt

        # Change direction periodically
        if self.wander_timer >= self.wander_interval:
            self.wander_direction = self._get_random_direction()
            self.wander_interval = random.uniform(1.0, 3.0)
            self.wander_timer = 0

        # Check for wall bounces
        if not self.is_growing:
            half_size = self.max_size / 2
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()

            # Bounce off walls by reversing direction
            if self.pos.x <= half_size or self.pos.x >= screen_width - half_size:
                self.wander_direction.x *= -1
                self.velocity.x *= -0.5  # Dampen velocity on bounce

            if self.pos.y <= half_size or self.pos.y >= screen_height - half_size:
                self.wander_direction.y *= -1
                self.velocity.y *= -0.5  # Dampen velocity on bounce

        return self.wander_direction
