import pygame
from entities.actor import Actor
from tags.tags import Tag


class Bullet(Actor):
    def __init__(
        self,
        owner_tags: Tag,
        screen: pygame.Surface,
        initial_pos: pygame.Vector2,
        direction: pygame.Vector2 = pygame.Vector2(1, 0),
        dmg: float = 25,
    ):
        super().__init__(screen, initial_pos)
        self.height = 20
        self.direction = direction.normalize()
        self.lifetime = 2.0
        self.dmg = dmg
        self.tags.append(Tag.BULLET)

        # Dimensions
        self.width = 70
        self.original_width = 70
        self.bullet_height = 35
        self.original_height = 35

        # Animation state
        self.is_shrinking = False
        self.shrink_duration = 0.05
        self.shrink_timer = 0

        # Collision state
        self.has_dealt_damage = False

        for tag in owner_tags:
            if tag not in self.tags:
                self.tags.append(tag)

    def _update_shrink_animation(self, dt: float):
        """Update the shrink animation and return True if animation is complete"""
        self.shrink_timer += dt
        progress = self.shrink_timer / self.shrink_duration

        if progress >= 1.0:
            return True  # Animation complete

        # Shrink both dimensions
        scale = 1 - progress
        self.width = self.original_width * scale
        self.bullet_height = self.original_height * scale
        return False  # Animation in progress

    def _start_shrink_animation(self):
        """Start the shrink animation"""
        if not self.is_shrinking:
            self.is_shrinking = True
            self.shrink_timer = 0

    def draw_shadow(self):
        angle = pygame.math.Vector2(1, 0).angle_to(self.direction)
        shadow_surface = pygame.Surface(
            (self.width, self.bullet_height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            shadow_surface, "black", (0, 0, self.width, self.bullet_height)
        )
        rotated_shadow = pygame.transform.rotate(shadow_surface, -angle)
        shadow_rect = rotated_shadow.get_rect(
            center=(self.pos.x, self.pos.y + self.height)
        )
        self.screen.blit(rotated_shadow, shadow_rect)

    def draw(self):
        angle = pygame.math.Vector2(1, 0).angle_to(self.direction)
        bullet_surface = pygame.Surface(
            (self.width, self.bullet_height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            bullet_surface, "yellow", (0, 0, self.width, self.bullet_height)
        )
        rotated_surface = pygame.transform.rotate(bullet_surface, -angle)
        rect = rotated_surface.get_rect(center=(self.pos.x, self.pos.y))
        self.screen.blit(rotated_surface, rect)

    def move(self, dt: float):
        # Handle shrinking animation
        if self.is_shrinking:
            animation_complete = self._update_shrink_animation(dt)
            if animation_complete and self.entity_manager:
                self.entity_manager.destroy(self)
            return  # Don't move while shrinking

        # Normal movement
        self.pos += self.direction * 1000 * dt

    def on_collision(self, other: Actor):
        # Don't collide with entities that share the same tags
        if any(tag in other.tags for tag in self.tags):
            return

        # Deal damage once
        if not self.has_dealt_damage:
            other.take_damage(self.dmg, self.pos)
            self.has_dealt_damage = True
            self._start_shrink_animation()
