import pygame
import random
from entities.static import Static
from tags.tags import Tag
import math


class Explosion(Static):
    def __init__(
        self,
        owner_tags: Tag,
        screen: pygame.Surface,
        initial_pos: pygame.Vector2,
        dmg: float = 10,
    ):
        super().__init__(screen, initial_pos)
        self.height = 20
        self.lifetime = 0.5  # Explosions last 0.5 second by default
        self.initial_lifetime = 0.5  # Store initial lifetime
        self.dmg = dmg
        self.max_size = 200
        self.size = 0  # Start at size 0
        self.grow_time = 0.1  # Time to reach max size

        # Secondary explosions - random number between 1 and 3
        self.secondary_explosions = self._create_secondary_explosions(initial_pos)

        for tag in owner_tags:
            if tag not in self.tags:  # Avoid duplicates
                self.tags.append(tag)

    def _create_secondary_explosions(self, initial_pos):
        """Create secondary explosions around the main explosion"""
        secondary_explosions = []
        num_secondary = random.randint(1, 3)

        # Distribute angles evenly around the circle
        angle_step = 360 / num_secondary
        start_angle = random.uniform(0, 360)

        for i in range(num_secondary):
            angle = (
                start_angle + (i * angle_step) + random.uniform(-30, 30)
            )  # Add some variance
            rad = math.radians(angle)
            distance = self.max_size * random.uniform(0.25, 0.4)  # Vary the distance

            offset_x = math.cos(rad) * distance
            offset_y = math.sin(rad) * distance

            secondary_explosions.append(
                {
                    "pos": pygame.Vector2(
                        initial_pos.x + offset_x, initial_pos.y + offset_y
                    ),
                    "max_size": self.max_size * random.uniform(0.4, 0.6),  # Vary size
                    "size": 0,
                    "delay": random.uniform(0.05, 0.15),  # Slight delay
                }
            )

        return secondary_explosions

    def _update_secondary_explosion_size(self, secondary, time_elapsed):
        """Update the size of a secondary explosion based on elapsed time"""
        if time_elapsed > secondary["delay"]:
            adjusted_time = time_elapsed - secondary["delay"]
            if adjusted_time < self.grow_time:
                progress = adjusted_time / self.grow_time
                secondary["size"] = secondary["max_size"] * progress
            else:
                shrink_time = self.initial_lifetime - self.grow_time
                time_since_max = adjusted_time - self.grow_time
                progress = time_since_max / shrink_time
                secondary["size"] = secondary["max_size"] * (1 - progress)

    def _draw_secondary_explosions(self, time_elapsed):
        """Draw all secondary explosions"""
        for secondary in self.secondary_explosions:
            if time_elapsed > secondary["delay"]:
                pygame.draw.circle(
                    self.screen, "orange", secondary["pos"], secondary["size"] / 2
                )

    def _draw_secondary_shadows(self, time_elapsed):
        """Draw shadows for all secondary explosions"""
        for secondary in self.secondary_explosions:
            if time_elapsed > secondary["delay"]:
                pygame.draw.circle(
                    self.screen,
                    "black",
                    (secondary["pos"].x, secondary["pos"].y + self.height),
                    secondary["size"] / 2,
                )

    def draw_shadow(self):
        # Main explosion shadow
        pygame.draw.circle(
            self.screen, "black", (self.pos.x, self.pos.y + self.height), self.size / 2
        )

        # Secondary explosion shadows
        time_elapsed = self.initial_lifetime - self.lifetime
        self._draw_secondary_shadows(time_elapsed)

    def draw(self):
        # Main explosion
        pygame.draw.circle(
            self.screen, "yellow", (self.pos.x, self.pos.y), self.size / 2
        )

        # Secondary explosions
        time_elapsed = self.initial_lifetime - self.lifetime
        self._draw_secondary_explosions(time_elapsed)

    def move(self, dt: float):
        # Calculate how much time has passed (initial - remaining)
        time_elapsed = self.initial_lifetime - self.lifetime

        # Update main explosion size
        if time_elapsed < self.grow_time:
            # Growing phase (fast)
            progress = time_elapsed / self.grow_time
            self.size = self.max_size * progress
        else:
            # Shrinking phase (slower)
            shrink_time = self.initial_lifetime - self.grow_time
            time_since_max = time_elapsed - self.grow_time
            progress = time_since_max / shrink_time
            # Inverse progress (1 to 0)
            self.size = self.max_size * (1 - progress)

        # Update secondary explosions
        for secondary in self.secondary_explosions:
            self._update_secondary_explosion_size(secondary, time_elapsed)

    def on_collision(self, other):
        # Don't collide with entities that share the same tags
        if any(tag in other.tags for tag in self.tags):
            return

        other.take_damage(self.dmg, self.pos)
