import pygame
from abc import ABC, abstractmethod
from entities.damage_number import DamageNumber
from entities.entity import Entity
from entities.explosion import Explosion
from tags.tags import Tag


class Actor(Entity, ABC):
    def __init__(
        self,
        screen: pygame.Surface,
        initial_pos: pygame.Vector2 = None,
    ):
        super().__init__()
        self.screen = screen
        self.pos = (
            initial_pos
            if initial_pos
            else pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        )
        self.velocity = pygame.Vector2(0, 0)  # Initialize as instance variable
        self.damage_flash_timer = 0
        self.damage_flash_duration = 0.15

        screen: pygame.Surface
        self.pos: pygame.Vector2
        self.height: int = 10
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 5000  # Units per second squared
        self.max_speed = 600  # Maximum speed
        self.friction = 5  # Deceleration factor
        self.layer = 1  # Rendering layer
        self.shadow_layer = 0  # All shadows render below actors
        self.invulnerable: bool = False
        self.invulnerable_timer: float = 0.0
        self.invulnerability_duration: float = (
            0.1  # Seconds of invulnerability after hit
        )

        self.collision_radius = 40
        self.hp = 100
        self.max_hp = 100
        self.dmg = 10

        self.look_direction = pygame.Vector2(1, 0)  # Direction the actor is facing

        self.original_sprite = None
        self.sprite = None
        self.sprite_size = 80

    def load_sprite(self, sprite_path: str, size: int = None):
        """Load and scale a sprite for this actor"""
        if size:
            self.sprite_size = size
        self.original_sprite = pygame.image.load(sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.original_sprite, (self.sprite_size, self.sprite_size)
        )

    def draw_sprite_shadow(self, direction: pygame.Vector2):
        """Draw a shadow for the sprite rotated to face the given direction"""
        if not self.sprite:
            return

        # Rotate sprite for shadow
        angle = pygame.math.Vector2(1, 0).angle_to(direction)
        rotated_sprite = pygame.transform.rotate(self.sprite, -angle)

        # Create darkened shadow
        shadow_surface = rotated_sprite.copy()
        shadow_surface.fill((0, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)

        shadow_rect = shadow_surface.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )
        self.screen.blit(shadow_surface, shadow_rect)

    def draw_sprite(
        self,
        direction: pygame.Vector2,
        flash_color: tuple = None,
        scale: tuple = (1.0, 1.0),
    ):
        """Draw the sprite rotated to face the given direction, with optional damage flash and scaling

        Args:
            direction: Direction vector the sprite should face
            flash_color: Optional RGB tuple for damage flash effect
            scale: Optional (scale_x, scale_y) tuple for sprite scaling
        """
        if not self.sprite:
            return None

        # Apply scaling if needed
        sprite_to_use = self.sprite
        if scale != (1.0, 1.0):
            scaled_width = int(self.sprite_size * scale[0])
            scaled_height = int(self.sprite_size * scale[1])
            sprite_to_use = pygame.transform.scale(
                self.original_sprite, (scaled_width, scaled_height)
            )

        # Calculate angle from direction
        angle = pygame.math.Vector2(1, 0).angle_to(direction)

        # Rotate the sprite
        rotated_sprite = pygame.transform.rotate(sprite_to_use, -angle)
        rect = rotated_sprite.get_rect(center=(self.pos.x, self.pos.y))

        # Draw the normal sprite
        self.screen.blit(rotated_sprite, rect)

        # Apply flash effect if taking damage
        if self.damage_flash_timer > 0 and flash_color:
            # Create a colored flash surface from the sprite
            flash_surface = rotated_sprite.copy()

            # Tint with flash color while preserving the shape
            flash_surface.fill(
                flash_color[:3] + (255,), special_flags=pygame.BLEND_RGB_MULT
            )
            # Then add color tint
            tint = (flash_color[0] // 2, flash_color[1] // 2, flash_color[2] // 2, 0)
            flash_surface.fill(tint, special_flags=pygame.BLEND_RGB_ADD)

            self.screen.blit(flash_surface, rect)

        return rotated_sprite, rect

    def draw_sprite_shadow_scaled(
        self, direction: pygame.Vector2, scale: tuple = (1.0, 1.0)
    ):
        """Draw a shadow for the sprite with optional scaling"""
        if not self.sprite:
            return

        # Apply scaling if needed
        sprite_to_use = self.sprite
        if scale != (1.0, 1.0):
            scaled_width = int(self.sprite_size * scale[0])
            scaled_height = int(self.sprite_size * scale[1])
            sprite_to_use = pygame.transform.scale(
                self.original_sprite, (scaled_width, scaled_height)
            )

        # Rotate sprite for shadow
        angle = pygame.math.Vector2(1, 0).angle_to(direction)
        rotated_sprite = pygame.transform.rotate(sprite_to_use, -angle)

        # Create darkened shadow
        shadow_surface = rotated_sprite.copy()
        shadow_surface.fill((0, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)

        shadow_rect = shadow_surface.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )
        self.screen.blit(shadow_surface, shadow_rect)

    def update_look_direction_from_velocity(self):
        """Update look_direction to face the direction of movement"""
        if self.velocity.length() > 0:
            self.look_direction = self.velocity.normalize()

    def update_look_direction_to_target(self, target_pos: pygame.Vector2):
        """Update look_direction to face a target position"""
        direction = target_pos - self.pos
        if direction.length() > 0:
            self.look_direction = direction.normalize()

    def get_color_with_flash(self, normal_color):
        """Returns the color to draw, with flash effect if taking damage"""
        if self.damage_flash_timer > 0:
            # Flash pattern: white -> red -> normal
            progress = 1 - (self.damage_flash_timer / self.damage_flash_duration)

            return "white"

        return normal_color

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def draw_shadow(self):
        """Each actor must implement their own shadow drawing for performance"""
        pass

    def apply_friction(self, dt: float):
        """Apply friction to velocity - shared physics logic"""
        if self.velocity.length() > 0:
            friction_amount = max(0, 1 - (self.friction * dt))
            self.velocity *= friction_amount

            # Stop completely if velocity is very small
            if self.velocity.length() < 5:
                self.velocity = pygame.Vector2(0, 0)

    def apply_acceleration(
        self, accel: pygame.Vector2, dt: float, clamp_to_max: bool = True
    ):
        """Apply acceleration and update velocity - shared physics logic"""
        if accel.length() > 0:
            accel = accel.normalize() * self.acceleration
            self.velocity += accel * dt
        else:
            # Apply friction when no acceleration
            self.apply_friction(dt)

        # Clamp velocity to max speed (but allow knockback to exceed temporarily)
        if (
            clamp_to_max
            and self.velocity.length() > self.max_speed
            and accel.length() > 0
        ):
            self.velocity = self.velocity.normalize() * self.max_speed

    def update_position(self, dt: float):
        """Update position based on velocity - shared physics logic"""
        self.pos += self.velocity * dt

    @abstractmethod
    def move(self, dt: float):
        pass

    def check_collision(self, other: "Actor") -> bool:
        distance = self.pos.distance_to(other.pos)
        return distance < (self.collision_radius + other.collision_radius)

    def on_collision(self, other: "Actor"):
        pass
        # print(f"Collision detected between {self} and {other}")

    def update(self, dt: float):
        # Update damage flash timer
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt

        self.draw_shadow()  # Draw shadow first
        self.draw()  # Then draw actor on top
        self.move(dt)

        # Update invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.invulnerable_timer = 0

        # Check collisions with all other entities
        if self.entity_manager:
            for entity in self.entity_manager.entities:
                if entity != self and isinstance(entity, Actor):
                    if self.check_collision(entity):
                        self.on_collision(entity)

    def die(self):
        self.hp = 0
        self.entity_manager.sound_manager.play_sound("explosion")
        explosion = Explosion([Tag.PLAYER], self.screen, self.pos.copy())
        self.entity_manager.instantiate(explosion)

        # Trigger camera shake on death/explosion
        if self.entity_manager.camera:
            self.entity_manager.camera.shake(15, 0.2)

        if Tag.ENEMY in self.tags:
            # Increase score for enemy death
            score = 100
            self.entity_manager.score += score
            damage_number = DamageNumber(self.screen, self.pos.copy(), score)
            self.entity_manager.instantiate(damage_number)

        self.entity_manager.destroy(self)

    def take_damage(
        self,
        amount: float,
        damage_source_pos: pygame.Vector2 = None,
        knockback_force=1000,
    ):
        if self.invulnerable:
            return

        self.hp -= amount
        self.damage_flash_timer = self.damage_flash_duration  # Start flash effect

        self.invulnerable = True
        self.invulnerable_timer = self.invulnerability_duration

        if damage_source_pos:
            # Calculate knockback direction (away from damage source)
            knockback_direction = self.pos - damage_source_pos
            if knockback_direction.length() > 0:
                knockback_direction = knockback_direction.normalize()
                # Apply knockback to velocity
                self.velocity += knockback_direction * knockback_force

        # Trigger camera shake (more intense for player)
        if self.entity_manager.camera:
            self.entity_manager.camera.shake(10, 0.1)

        if self.hp <= 0:
            self.die()
            return

        self.entity_manager.sound_manager.play_sound("hit")
