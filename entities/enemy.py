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
        self.load_sprite("assets/sprites/enemy.png", self.max_size)

    def draw_shadow(self):
        # Calculate scale based on growth animation
        if self.is_growing:
            scale = self.current_size / self.max_size
        else:
            scale = 1.0

        self.draw_sprite_shadow_scaled(self.look_direction, scale=(scale, scale))

    def draw(self):
        # Calculate scale based on growth animation
        if self.is_growing:
            scale = self.current_size / self.max_size
        else:
            scale = 1.0

        # Use the base class sprite drawing method with scaling
        self.draw_sprite(
            self.look_direction, flash_color=(255, 100, 100), scale=(scale, scale)
        )

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

        self.update_look_direction_from_velocity()

        self.update_position(dt)

    def on_collision(self, other: Actor):
        if any(tag in other.tags for tag in self.tags):
            return

        other.take_damage(self.dmg, self.pos)
