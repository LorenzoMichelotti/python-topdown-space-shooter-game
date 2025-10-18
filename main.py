# Example file showing a basic pygame "game loop"
import pygame

from entities.cursor import Cursor
from entities.enemy import Enemy
from entities.player import Player
from systems.entity_manager import EntityManager
from systems.sound_manager import SoundManager
from systems.wave_manager import WaveManager

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0  # Delta time between frames

# load entities
player = Player(screen)
enemy = Enemy(
    screen, pygame.Vector2(screen.get_width() / 2 - 200, screen.get_height() / 2)
)
sound_manager = SoundManager()
entity_manager = EntityManager(sound_manager=sound_manager)
wave_manager = WaveManager(entity_manager, screen)
cursor = Cursor(screen)


def setup():
    pygame.mouse.set_visible(False)
    # entity_manager.instantiate(enemy)
    sound_manager.load_sound("shoot", "assets/sounds/Shoot6.wav", 0.1)
    sound_manager.load_sound("explosion", "assets/sounds/Boom10.wav")
    sound_manager.load_sound("hit", "assets/sounds/Hit.wav")

    entity_manager.instantiate(player)
    entity_manager.instantiate(cursor)

    wave_manager.start_next_wave()


def render():
    screen.fill("blue")

    entity_manager.update(dt)
    wave_manager.update(dt)

    pygame.display.flip()


setup()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    render()

    dt = clock.tick(144) / 1000

pygame.quit()
