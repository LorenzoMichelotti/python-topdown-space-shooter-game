from entities.entity import Entity


class EntityManager:
    def __init__(self, sound_manager=None):
        self.entities: list[Entity] = []
        self.sound_manager = sound_manager

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
        # Sort entities by layer before updating
        self.entities.sort(key=lambda e: getattr(e, "layer", 0))

        for entity in self.entities:
            if entity.lifetime != -1:
                entity.lifetime -= dt
                if entity.lifetime <= 0:
                    self.destroy(entity)
                    continue
            entity.update(dt)
