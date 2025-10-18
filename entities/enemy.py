import pygame
from entities.actor import Actor
from tags.tags import Tag


class Enemy(Actor):
    def __init__(self, screen: pygame.Surface, initial_pos: pygame.Vector2):
        super().__init__(screen, initial_pos)
        self.height = 10
        self.layer = 2
        self.max_speed = 150
        self.acceleration = 1000
        self.friction = 3
        self.size = 80  # Size of the square
        self.tags.append(Tag.ENEMY)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0  # Current rotation angle

    def draw_shadow(self):
        # Create a rotated shadow surface
        shadow_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, "black", (0, 0, self.size, self.size))

        rotated_shadow = pygame.transform.rotate(shadow_surface, -self.rotation)
        shadow_rect = rotated_shadow.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )
        self.screen.blit(rotated_shadow, shadow_rect)

    def draw(self):
        color = self.get_color_with_flash("red")

        # Create a surface for the square
        square_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, color, (0, 0, self.size, self.size))

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(square_surface, -self.rotation)
        rect = rotated_surface.get_rect(center=(self.pos.x, self.pos.y))

        self.screen.blit(rotated_surface, rect)

    def move(self, dt: float):
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

        if player:
            # Calculate direction to player
            direction = player.pos - self.pos
            distance = direction.length()

            # Only chase if not too close
            if distance > self.collision_radius:
                direction = direction.normalize()
                # Add acceleration toward player
                self.velocity += direction * self.acceleration * dt

        # Apply friction to slow down
        if self.velocity.length() > 0:
            # Update rotation based on velocity direction
            self.rotation = pygame.math.Vector2(1, 0).angle_to(self.velocity)

            friction_amount = 1 - (self.friction * dt)
            if friction_amount < 0:
                friction_amount = 0
            self.velocity *= friction_amount

        # Clamp velocity to max speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        # Update position using velocity (this allows knockback to work)
        self.pos += self.velocity * dt
