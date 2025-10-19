import pygame
from entities.base_enemy import BaseEnemy


class Dasher(BaseEnemy):
    """Enemy that telegraphs a line then dashes toward the player once"""

    def __init__(self, screen: pygame.Surface, initial_pos: pygame.Vector2):
        super().__init__(screen, initial_pos)
        self.max_speed = 1000

        # Dasher-specific properties
        self.telegraph_duration = 0.5  # How long to show the line before dashing
        self.telegraph_timer = 0
        self.has_dashed = False  # Track if we've already dashed
        self.dash_direction = None  # Store the dash direction

        # Line endpoints for telegraph
        self.line_start = None
        self.line_end = None

    def draw(self):
        """Draw dasher with cyan color and telegraph line"""
        # Draw telegraph line if haven't dashed yet
        if not self.has_dashed and self.line_start and self.line_end:
            line_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            line_color = (255, 0, 0)  # Red color
            pygame.draw.line(
                line_surface, line_color, self.line_start, self.line_end, 20
            )
            self.screen.blit(line_surface, (0, 0))

        # Draw sprite with cyan tint
        self.draw_sprite_with_color(color_tint=(100, 255, 255))

    def calculate_acceleration(self, dt: float) -> pygame.Vector2:
        """Telegraph, dash once toward player, then chase normally"""
        # Don't move while growing
        if self.is_growing:
            return pygame.Vector2(0, 0)

        # Find player
        from entities.player import Player

        players = [
            entity
            for entity in self.entity_manager.entities
            if isinstance(entity, Player)
        ]

        if not players:
            return pygame.Vector2(0, 0)

        player = players[0]

        # If haven't dashed yet, telegraph
        if not self.has_dashed:
            self.telegraph_timer += dt
            direction_to_player = (player.pos - self.pos).normalize()

            # Update telegraph line
            line_length = 2000
            self.line_start = self.pos.copy()
            self.line_end = self.pos + (direction_to_player * line_length)

            # When telegraph is done, start the dash
            if self.telegraph_timer >= self.telegraph_duration:
                self.has_dashed = True
                self.dash_direction = direction_to_player
                self.velocity = self.dash_direction * self.max_speed

            return pygame.Vector2(0, 0)  # Don't accelerate during telegraph

        # After dash started, keep moving in that direction
        if self.dash_direction is None:
            return pygame.Vector2(0, 0)

        # Detect if hit edge of screen
        half_size = self.max_size / 2
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        if (
            self.pos.x <= half_size + 5
            or self.pos.x >= screen_width - half_size - 5
            or self.pos.y <= half_size + 5
            or self.pos.y >= screen_height - half_size - 5
        ):
            # Stop dashing and prepare to telegraph again
            self.has_dashed = False
            self.telegraph_timer = 0
            self.dash_direction = None
            return pygame.Vector2(0, 0)

        return self.dash_direction * self.acceleration
