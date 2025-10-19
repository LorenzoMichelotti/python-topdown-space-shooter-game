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
            0.2  # Seconds of invulnerability after hit
        )

        self.collision_radius = 40
        self.hp = 100
        self.max_hp = 100
        self.dmg = 10

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
