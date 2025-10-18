import random
import pygame
from entities.enemy import Enemy
from systems.entity_manager import EntityManager


class WaveManager:
    def __init__(self, entity_manager: EntityManager, screen: pygame.Surface):
        self.entity_manager = entity_manager
        self.screen = screen
        self.waves = [
            {"enemy_count": 5, "spawn_interval": 1.0},
            {"enemy_count": 10, "spawn_interval": 0.8},
            {"enemy_count": 15, "spawn_interval": 0.5},
        ]
        self.current_wave_index = -1
        self.enemies_spawned = 0
        self.time_since_last_spawn = 0.0
        self.wave_in_progress = False

    def start_next_wave(self):
        self.current_wave_index += 1
        if self.current_wave_index < len(self.waves):
            self.enemies_spawned = 0
            self.time_since_last_spawn = 0.0
            self.wave_in_progress = True
        else:
            print("All waves completed!")

    def update(self, dt: float):
        if not self.wave_in_progress:
            return

        current_wave = self.waves[self.current_wave_index]
        if self.enemies_spawned < current_wave["enemy_count"]:
            self.time_since_last_spawn += dt
            if self.time_since_last_spawn >= current_wave["spawn_interval"]:
                self.spawn_enemy()
                self.enemies_spawned += 1
                self.time_since_last_spawn = 0.0
        else:
            # Check if all enemies are defeated
            if not any(
                isinstance(entity, Enemy) for entity in self.entity_manager.entities
            ):
                self.wave_in_progress = False
                print(f"Wave {self.current_wave_index + 1} completed!")
                self.start_next_wave()

    def spawn_enemy(self):
        enemy = Enemy(
            self.screen, pygame.Vector2(random.randint(0, self.screen.get_width()), 0)
        )
        self.entity_manager.instantiate(enemy)
