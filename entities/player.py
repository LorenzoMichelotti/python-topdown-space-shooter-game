import pygame
import random
from entities.actor import Actor
from entities.bullet import Bullet
from tags.tags import Tag


class Player(Actor):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.look_direction = pygame.Vector2(1, 0)
        self.pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        self.shoot_cooldown = 0  # Cooldown timer
        self.shoot_delay = 0.2  # Seconds between shots
        self.shoot_angle_variance = 10  # Degrees of inaccuracy
        self.layer = 3
        self.size = 80
        self.height = 20
        self.tags.append(Tag.PLAYER)
        self.bullet_count = 3  # Number of bullets per shot
        self.original_sprite = pygame.image.load(
            "assets/sprites/ship_sprite.png"
        ).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.original_sprite, (self.size, self.size)
        )

        # Trail effect
        self.trail_particles = []
        self.trail_spawn_timer = 0
        self.trail_spawn_interval = 0.01  # Spawn trail particle every 0.03 seconds

    def draw_shadow(self):
        # Rotate sprite for shadow
        angle = pygame.math.Vector2(1, 0).angle_to(self.look_direction)
        rotated_sprite = pygame.transform.rotate(self.sprite, -angle)

        # Create darkened shadow
        shadow_surface = rotated_sprite.copy()
        shadow_surface.fill((0, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)

        shadow_rect = shadow_surface.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )
        self.screen.blit(shadow_surface, shadow_rect)

    def _update_trail(self, dt: float):
        """Update trail particles"""
        # Update existing particles
        for particle in self.trail_particles[:]:
            particle["lifetime"] -= dt

            if particle["lifetime"] <= 0:
                self.trail_particles.remove(particle)
                continue

            # Calculate size based on lifetime
            progress = particle["lifetime"] / particle["max_lifetime"]
            if progress > 0.9:
                # Growing phase
                growth = (1 - progress) * 2  # 0 to 1
                particle["size"] = particle["max_size"] * growth
            else:
                # Shrinking phase
                particle["size"] = particle["max_size"] * (progress * 2)

    def _draw_trail(self):
        """Draw trail particles"""
        for particle in self.trail_particles:
            if particle["size"] > 0:
                pygame.draw.circle(
                    self.screen,
                    particle["color"],
                    (int(particle["pos"].x), int(particle["pos"].y)),
                    int(particle["size"] / 2),
                )

    def _spawn_trail_particle(self):
        """Spawn a new trail particle at player position"""
        # Spawn behind the player based on their movement direction
        offset = self.look_direction * -20  # 20 pixels behind
        spawn_pos = self.pos + offset

        particle = {
            "pos": spawn_pos.copy(),
            "size": 20,
            "max_size": 20,
            "lifetime": 0.5,  # Total lifetime in seconds
            "max_lifetime": 0.5,
            "color": (155, 255, 100),  # Light blue with some transparency
        }
        self.trail_particles.append(particle)

    def draw(self):
        # Draw trail first (behind the ship)
        self._draw_trail()

        # Calculate angle from look direction
        angle = pygame.math.Vector2(1, 0).angle_to(self.look_direction)

        # Rotate the sprite
        rotated_sprite = pygame.transform.rotate(self.sprite, -angle)
        rect = rotated_sprite.get_rect(center=(self.pos.x, self.pos.y))

        # Draw the normal sprite
        self.screen.blit(rotated_sprite, rect)

        # Apply flash effect if taking damage - red sprite overlay
        if self.damage_flash_timer > 0:
            # Create a red flash surface from the sprite
            flash_surface = rotated_sprite.copy()

            # Tint red while preserving the shape
            # First multiply to remove other colors
            flash_surface.fill(
                (255, 100, 100, 255), special_flags=pygame.BLEND_RGB_MULT
            )
            # Then add red tint
            flash_surface.fill((150, 0, 0, 0), special_flags=pygame.BLEND_RGB_ADD)

            self.screen.blit(flash_surface, rect)

    def move(self, dt: float):
        keys = pygame.key.get_pressed()

        # Calculate acceleration direction from input
        accel = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            accel.y -= 1
        if keys[pygame.K_s]:
            accel.y += 1
        if keys[pygame.K_a]:
            accel.x -= 1
        if keys[pygame.K_d]:
            accel.x += 1

        # Apply physics (shared logic)
        self.apply_acceleration(accel, dt)
        self.update_position(dt)

        # Update look direction to mouse
        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_pos[0] - self.pos.x, mouse_pos[1] - self.pos.y)
        if direction.length() > 0:
            self.look_direction = direction.normalize()

        # Update trail
        self._update_trail(dt)

        # Spawn trail particles while moving
        if self.velocity.length() > 10:  # Only spawn when moving
            self.trail_spawn_timer += dt
            if self.trail_spawn_timer >= self.trail_spawn_interval:
                self._spawn_trail_particle()
                self.trail_spawn_timer = 0

    def spawn_bullet(self, angle_offset: float):
        bullet = Bullet(
            self.tags.copy(),
            self.screen,
            self.pos.copy(),
            self.look_direction.copy().rotate(
                angle_offset
                + random.uniform(-self.shoot_angle_variance, self.shoot_angle_variance)
            ),
        )
        self.entity_manager.instantiate(bullet)

    def shoot(self):
        if self.shoot_cooldown <= 0:
            for _ in range(self.bullet_count):
                # add slight spread for multiple bullets
                angle_offset = random.uniform(
                    -self.shoot_angle_variance, self.shoot_angle_variance
                )
                self.spawn_bullet(angle_offset)
            self.shoot_cooldown = self.shoot_delay
            self.entity_manager.sound_manager.play_sound("shoot")

    def update(self, dt: float):
        super().update(dt)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if pygame.mouse.get_pressed()[0]:
            self.shoot()
