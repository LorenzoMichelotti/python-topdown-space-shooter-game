# Example file showing a basic pygame "game loop"
import pygame

from entities.cursor import Cursor
from entities.enemy import Enemy
from entities.player import Player
from scenes.scene import Scene
from systems.entity_manager import EntityManager
from systems.sound_manager import SoundManager
from systems.wave_manager import WaveManager


class Level(Scene):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        # load entities
        self.player = Player(screen)
        self.enemy = Enemy(
            screen,
            pygame.Vector2(screen.get_width() / 2 - 200, screen.get_height() / 2),
        )
        self.sound_manager = SoundManager()
        self.entity_manager = EntityManager(sound_manager=self.sound_manager)
        self.wave_manager = WaveManager(
            entity_manager=self.entity_manager, screen=screen
        )
        self.cursor = Cursor(screen)

    def setup(self):
        pygame.mouse.set_visible(False)
        # entity_manager.instantiate(enemy)
        self.sound_manager.load_sound("shoot", "assets/sounds/Shoot6.wav", 0.1)
        self.sound_manager.load_sound("explosion", "assets/sounds/Boom10.wav")
        self.sound_manager.load_sound("hit", "assets/sounds/Hit.wav")

        self.entity_manager.instantiate(self.player)
        self.entity_manager.instantiate(self.cursor)

        self.wave_manager.start_next_wave()

    def render(self, dt: float):
        self.screen.fill("blue")

        self.entity_manager.update(dt)
        self.wave_manager.update(dt)

        pygame.display.flip()
