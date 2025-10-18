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
        self.size = 40  # Triangle size
        self.tags.append(Tag.PLAYER)

    def draw_shadow(self):
        # Create shadow triangle points
        angle = pygame.math.Vector2(1, 0).angle_to(self.look_direction)

        # Define triangle points (pointing right initially)
        points = [
            pygame.Vector2(self.size, 0),  # Front point
            pygame.Vector2(-self.size * 0.6, -self.size * 0.8),  # Back left
            pygame.Vector2(-self.size * 0.6, self.size * 0.8),  # Back right
        ]

        # Rotate and offset each point for shadow
        rotated_points = []
        for point in points:
            rotated = point.rotate(angle)
            rotated_points.append(
                (self.pos.x + rotated.x, self.pos.y + rotated.y + self.height)
            )

        pygame.draw.polygon(self.screen, "black", rotated_points)

    def draw(self):
        color = self.get_color_with_flash("white")

        # Calculate angle from look direction
        angle = pygame.math.Vector2(1, 0).angle_to(self.look_direction)

        # Define triangle points (pointing right initially)
        points = [
            pygame.Vector2(self.size, 0),  # Front point
            pygame.Vector2(-self.size * 0.5, -self.size * 0.8),  # Back left
            pygame.Vector2(-self.size * 0.5, self.size * 0.8),  # Back right
        ]

        # Rotate and offset each point
        rotated_points = []
        for point in points:
            rotated = point.rotate(angle)
            rotated_points.append((self.pos.x + rotated.x, self.pos.y + rotated.y))

        pygame.draw.polygon(self.screen, color, rotated_points)

    def move(self, dt: float):
        keys = pygame.key.get_pressed()

        # Calculate acceleration direction
        accel = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            accel.y -= 1
        if keys[pygame.K_s]:
            accel.y += 1
        if keys[pygame.K_a]:
            accel.x -= 1
        if keys[pygame.K_d]:
            accel.x += 1

        # Normalize diagonal movement
        if accel.length() > 0:
            accel = accel.normalize() * self.acceleration
            self.velocity += accel * dt
        else:
            # Apply friction when no input
            if self.velocity.length() > 0:
                friction_force = (
                    self.velocity.normalize() * self.friction * self.acceleration * dt
                )
                if friction_force.length() > self.velocity.length():
                    self.velocity = pygame.Vector2(0, 0)
                else:
                    self.velocity -= friction_force

        # Clamp velocity to max speed
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        # Update position
        self.pos += self.velocity * dt

        # Update look direction to mouse
        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_pos[0] - self.pos.x, mouse_pos[1] - self.pos.y)
        if direction.length() > 0:
            self.look_direction = direction.normalize()

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet = Bullet(
                self.tags.copy(),
                self.screen,
                self.pos.copy(),
                self.look_direction.copy().rotate(
                    random.uniform(
                        -self.shoot_angle_variance, self.shoot_angle_variance
                    )
                ),
            )
            self.entity_manager.instantiate(bullet)
            self.shoot_cooldown = self.shoot_delay
            self.entity_manager.sound_manager.play_sound("shoot")

    def update(self, dt: float):
        super().update(dt)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if pygame.mouse.get_pressed()[0]:
            self.shoot()
