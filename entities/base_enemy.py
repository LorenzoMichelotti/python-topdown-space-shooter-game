import pygame
import random
from abc import abstractmethod
from entities.actor import Actor
from tags.tags import Tag


class BaseEnemy(Actor):
    """Base class for all enemy types with shared grow animation and rendering"""

    def __init__(self, screen: pygame.Surface, initial_pos: pygame.Vector2):
        super().__init__(screen, initial_pos)
        self.layer = 2
        self.friction = 3

        # Random size between 60 and 100
        self.max_size = random.randint(60, 100)
        self.size = 0
        self.current_size = 0
        self.grow_duration = 0.2
        self.grow_timer = 0
        self.is_growing = True
        self.tags.append(Tag.ENEMY)
        self.velocity = pygame.Vector2(0, 0)

        # Scale HP based on size (60 size = 60 HP, 80 size = 100 HP, 100 size = 150 HP)
        # Using a formula: HP scales from 60 to 150 as size goes from 60 to 100
        size_ratio = (self.max_size - 60) / 40  # 0.0 to 1.0
        self.hp = 60 + (size_ratio * 90)  # 60 to 150 HP
        self.max_hp = self.hp

        # Load sprite at max size
        self.load_sprite("assets/sprites/enemy.png", self.max_size)

    def get_growth_scale(self):
        """Get the current scale based on growth animation"""
        if self.is_growing:
            return self.current_size / self.max_size
        return 1.0

    def update_growth(self, dt: float):
        """Update growth animation"""
        if self.is_growing:
            self.grow_timer += dt
            progress = min(1.0, self.grow_timer / self.grow_duration)
            self.current_size = self.max_size * progress

            if progress >= 1.0:
                self.is_growing = False
                self.current_size = self.max_size

    def clamp_to_screen(self):
        """Clamp position to screen boundaries (only after fully grown)"""
        if not self.is_growing:
            half_size = self.max_size / 2
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()

            self.pos.x = max(half_size, min(self.pos.x, screen_width - half_size))
            self.pos.y = max(half_size, min(self.pos.y, screen_height - half_size))

    def draw_shadow(self):
        """Draw shadow with growth scaling"""
        scale = self.get_growth_scale()
        self.draw_sprite_shadow_scaled(self.look_direction, scale=(scale, scale))

    def draw_sprite_with_color(self, color_tint: tuple = None):
        """Draw sprite with optional color modulation and growth scaling

        Args:
            color_tint: Optional RGB tuple to tint the sprite (e.g., (255, 255, 100) for yellow)
        """
        scale = self.get_growth_scale()

        if color_tint:
            # Manual color modulation
            if not self.sprite:
                return

            # Apply scaling if needed
            sprite_to_use = self.sprite
            if scale != 1.0:
                scaled_width = int(self.sprite_size * scale)
                scaled_height = int(self.sprite_size * scale)
                sprite_to_use = pygame.transform.scale(
                    self.original_sprite, (scaled_width, scaled_height)
                )

            # Calculate angle from direction
            angle = pygame.math.Vector2(1, 0).angle_to(self.look_direction)

            # Rotate the sprite
            rotated_sprite = pygame.transform.rotate(sprite_to_use, -angle)

            # Create color-tinted version
            tinted_sprite = rotated_sprite.copy()
            tinted_sprite.fill(color_tint + (255,), special_flags=pygame.BLEND_RGB_MULT)

            rect = tinted_sprite.get_rect(center=(self.pos.x, self.pos.y))
            self.screen.blit(tinted_sprite, rect)

            # Apply flash effect if taking damage - red flash overlay
            if self.damage_flash_timer > 0:
                flash_surface = tinted_sprite.copy()
                # Tint red while preserving the shape
                flash_surface.fill(
                    (255, 100, 100, 255), special_flags=pygame.BLEND_RGB_MULT
                )
                # Then add red tint
                flash_surface.fill((150, 0, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
                self.screen.blit(flash_surface, rect)
        else:
            # Use standard draw with flash color
            self.draw_sprite(
                self.look_direction, flash_color=(255, 100, 100), scale=(scale, scale)
            )

    @abstractmethod
    def calculate_acceleration(self, dt: float) -> pygame.Vector2:
        """Calculate acceleration for this frame - must be implemented by subclasses"""
        pass

    def move(self, dt: float):
        """Shared movement logic - subclasses override calculate_acceleration"""
        # Handle growth animation
        self.update_growth(dt)

        # Get acceleration from subclass (different for each enemy type)
        accel = self.calculate_acceleration(dt)

        # Apply physics
        self.apply_acceleration(accel, dt, clamp_to_max=False)

        # Clamp to max speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        # Update look direction
        self.update_look_direction_from_velocity()

        # Update position
        self.update_position(dt)

        # Clamp to screen
        self.clamp_to_screen()

    def on_collision(self, other: Actor):
        """Standard collision behavior for all enemies"""
        # Don't collide with entities that share the same tags
        if any(tag in other.tags for tag in self.tags):
            return

        other.take_damage(self.dmg, self.pos)
