# Example file showing a basic pygame "game loop"
import pygame
from enum import Enum

from entities.cursor import Cursor
from entities.enemy import Enemy
from entities.player import Player
from scenes.level import Level
from systems.entity_manager import EntityManager
from systems.sound_manager import SoundManager
from systems.wave_manager import WaveManager
from ui.main_menu import MainMenu

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0  # Delta time between frames

current_scene = None


def switch_scene(new_scene):
    global current_scene
    current_scene = new_scene
    current_scene.setup()


switch_scene(MainMenu(screen, switch_scene))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_scene.render(dt)

    dt = clock.tick(144) / 1000

pygame.quit()
