import pygame
import random


class Camera:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.offset = pygame.Vector2(0, 0)
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0

    def shake(self, intensity: float, duration: float):
        """Apply camera shake with given intensity and duration"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration

    def apply_shake(self, intensity: float, duration: float):
        """Alias for shake() method"""
        self.shake(intensity, duration)

    def update(self, dt: float):
        """Update camera shake"""
        if self.shake_timer > 0:
            self.shake_timer -= dt

            # Calculate shake offset
            progress = self.shake_timer / self.shake_duration
            current_intensity = self.shake_intensity * progress

            # Random shake offset
            self.offset.x = random.uniform(-current_intensity, current_intensity)
            self.offset.y = random.uniform(-current_intensity, current_intensity)
        else:
            # No shake, reset offset
            self.offset.x = 0
            self.offset.y = 0

    def get_offset(self) -> pygame.Vector2:
        """Get current camera offset for rendering"""
        return self.offset
