from entities.static import Static
import pygame

from tags.tags import Tag


class Blast(Static):
    # created a growing explosion circle that damages all enemies once when it touches them
    def __init__(
        self,
        screen: pygame.Surface,
        initial_pos: pygame.Vector2,
        max_size: float = 3000,
        grow_time: float = 0.2,
        initial_lifetime: float = 0.5,
    ):
        super().__init__(screen, initial_pos)
        self.lifetime = initial_lifetime  # Total lifetime
        self.initial_lifetime = initial_lifetime  # Store initial lifetime
        self.max_size = max_size
        self.size = 0  # Start at size 0
        self.grow_time = grow_time  # Time to reach max size
        self.damaged_entities = set()  # Track which entities we've already damaged

    def update(self, dt: float):
        super().update(dt)

        # Grow size over grow_time
        if self.size < self.max_size:
            growth_rate = self.max_size / self.grow_time
            self.size += growth_rate * dt
            if self.size > self.max_size:
                self.size = self.max_size
                self.on_expire()

        # Check for collisions with enemies to apply damage
        if self.entity_manager:
            for entity in self.entity_manager.entities:
                if (
                    entity not in self.damaged_entities
                    and hasattr(entity, "take_damage")
                    and Tag.ENEMY in entity.tags
                ):
                    distance = (entity.pos - self.pos).length()
                    if distance < (self.size / 2 + entity.collision_radius):
                        entity.take_damage(1000)  # Apply damage
                        self.damaged_entities.add(entity)  # Mark as damaged

    def draw(self):
        # Draw explosion as a opaque white circle
        explosion_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(
            explosion_surface,
            (255, 255, 255, 255),  # White with full opacity
            (self.size / 2, self.size / 2),
            self.size / 2,
        )
        self.screen.blit(
            explosion_surface,
            (self.pos.x - self.size / 2, self.pos.y - self.size / 2),
        )

    def draw_shadow(self):
        # Draw shadow as a opaque black circle
        shadow_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(
            shadow_surface,
            (0, 0, 0, 255),  # Black with full opacity
            (self.size / 2, self.size / 2),
            self.size / 2,
        )
        self.screen.blit(
            shadow_surface,
            (self.pos.x - self.size / 2, self.pos.y - self.size / 2 + 10),
        )

    def move(self, dt: float):
        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.on_expire()

    def on_collision(self, other):
        pass  # Blast does not react to collisions

    def on_expire(self):
        self.entity_manager.destroy(self)
