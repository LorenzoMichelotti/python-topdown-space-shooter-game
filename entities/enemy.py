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
        self.max_size = 80  # Maximum size of the square
        self.size = 0  # Start at size 0
        self.current_size = 0  # Current size during growth
        self.grow_duration = 0.2  # Time to grow to full size
        self.grow_timer = 0  # Timer for growth animation
        self.is_growing = True  # Flag to track if still growing
        self.tags.append(Tag.ENEMY)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0  # Current rotation angle

    def draw_shadow(self):
        # Create a rotated shadow surface using current_size
        if self.current_size <= 0:
            return  # Don't draw shadow if size is 0

        shadow_surface = pygame.Surface(
            (self.current_size, self.current_size), pygame.SRCALPHA
        )
        pygame.draw.rect(
            shadow_surface, "black", (0, 0, self.current_size, self.current_size)
        )

        rotated_shadow = pygame.transform.rotate(shadow_surface, -self.rotation)
        shadow_rect = rotated_shadow.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )
        self.screen.blit(rotated_shadow, shadow_rect)

    def draw(self):
        # Don't draw if size is 0
        if self.current_size <= 0:
            return

        color = self.get_color_with_flash("red")

        # Create a surface for the square using current_size
        square_surface = pygame.Surface(
            (self.current_size, self.current_size), pygame.SRCALPHA
        )
        pygame.draw.rect(
            square_surface, color, (0, 0, self.current_size, self.current_size)
        )

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(square_surface, -self.rotation)
        rect = rotated_surface.get_rect(center=(self.pos.x, self.pos.y))

        self.screen.blit(rotated_surface, rect)

    def move(self, dt: float):
        # Handle growth animation
        if self.is_growing:
            self.grow_timer += dt
            progress = min(1.0, self.grow_timer / self.grow_duration)
            self.current_size = self.max_size * progress

            if progress >= 1.0:
                self.is_growing = False
                self.current_size = self.max_size

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

        # Apply physics (shared logic)
        self.apply_acceleration(accel, dt, clamp_to_max=False)

        # Custom max speed clamping for enemy (only when chasing)
        if self.velocity.length() > self.max_speed and player:
            distance_to_player = (player.pos - self.pos).length()
            if distance_to_player > self.collision_radius:
                self.velocity = self.velocity.normalize() * self.max_speed

        # Update rotation based on velocity direction
        if self.velocity.length() > 0:
            self.rotation = pygame.math.Vector2(1, 0).angle_to(self.velocity)

        self.update_position(dt)

    def on_collision(self, other: Actor):
        # Don't collide with entities that share the same tags
        if any(tag in other.tags for tag in self.tags):
            return

        other.take_damage(self.dmg, self.pos)
