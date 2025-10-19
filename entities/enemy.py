import pygame
from entities.base_enemy import BaseEnemy
from entities.actor import Actor
from tags.tags import Tag


class Enemy(BaseEnemy):
    """Standard enemy that chases the player"""

    def __init__(self, screen: pygame.Surface, initial_pos: pygame.Vector2):
        super().__init__(screen, initial_pos)
        self.max_speed = 150
        self.acceleration = 1000

    def draw(self):
        self.draw_sprite_with_color()

    def calculate_acceleration(self, dt: float) -> pygame.Vector2:
        # Find the player
        player = None
        if self.entity_manager:
            for entity in self.entity_manager.entities:
                if (
                    isinstance(entity, Actor)
                    and Tag.PLAYER in entity.tags
                    and Tag.BULLET not in entity.tags
                ):
                    player = entity
                    break

        # Don't chase while growing
        accel = pygame.Vector2(0, 0)
        if player and not self.is_growing:
            direction = player.pos - self.pos
            distance = direction.length()

            # Only chase if not too close
            if distance > self.collision_radius:
                accel = direction.normalize()

        return accel
