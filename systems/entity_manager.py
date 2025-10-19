from entities.entity import Entity
import pygame


class EntityManager:
    def __init__(self, sound_manager=None):
        self.entities: list[Entity] = []
        self.sound_manager = sound_manager
        self.score = 0
        self.paused = False
        self.pause_key_timer = 0  # Timer for pause key debounce

    def instantiate(self, entity: Entity, lifetime: float = -1):
        entity.entity_manager = self
        if lifetime != -1:
            entity.lifetime = lifetime
        self.entities.append(entity)
        # Sort immediately after adding to maintain layer order
        self.entities.sort(key=lambda e: getattr(e, "layer", 0))

    def destroy(self, entity: Entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def update(self, dt: float):
        # Update pause key debounce timer
        if self.pause_key_timer > 0:
            self.pause_key_timer -= dt

        # Handle pause toggle with proper debounce
        if pygame.key.get_pressed()[pygame.K_ESCAPE] and self.pause_key_timer <= 0:
            self.paused = not self.paused
            self.pause_key_timer = 0.2  # 200ms debounce

        # Sort entities by layer before updating
        self.entities.sort(key=lambda e: getattr(e, "layer", 0))

        for entity in self.entities:
            if not self.paused and entity.lifetime != -1:
                entity.lifetime -= dt
                if entity.lifetime <= 0:
                    self.destroy(entity)
                    continue
            entity.update(dt)
