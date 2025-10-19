import random
import pygame
from entities.enemy import Enemy
from systems.entity_manager import EntityManager


class WaveManager:
    def __init__(self, entity_manager: EntityManager, screen: pygame.Surface):
        self.entity_manager = entity_manager
        self.screen = screen
        self.current_wave_index = 0
        self.enemies_spawned = 0
        self.time_since_last_spawn = 0.0
        self.wave_in_progress = False

    def get_wave_config(self, wave_number: int):
        """Generate wave configuration based on wave number for infinite scaling"""
        # Base values
        base_enemy_count = 5
        base_spawn_interval = 1.0
        
        # Scale enemy count: increases by 3 every wave, with diminishing returns
        enemy_count = base_enemy_count + (wave_number * 3)
        
        # Scale spawn interval: gets faster but has a minimum of 0.1 seconds
        spawn_interval = max(0.1, base_spawn_interval - (wave_number * 0.05))
        
        return {
            "enemy_count": enemy_count,
            "spawn_interval": spawn_interval
        }

    def start_next_wave(self):
        self.current_wave_index += 1
        self.enemies_spawned = 0
        self.time_since_last_spawn = 0.0
        self.wave_in_progress = True
        
        wave_config = self.get_wave_config(self.current_wave_index)
        print(f"Wave {self.current_wave_index} starting! Enemies: {wave_config['enemy_count']}, Spawn Interval: {wave_config['spawn_interval']:.2f}s")

    def update(self, dt: float):
        if not self.wave_in_progress:
            return

        current_wave = self.get_wave_config(self.current_wave_index)
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
                print(f"Wave {self.current_wave_index} completed!")
                self.start_next_wave()

    def spawn_enemy(self):
        enemy = Enemy(
            self.screen, pygame.Vector2(random.randint(0, self.screen.get_width()), 0)
        )
        self.entity_manager.instantiate(enemy)
