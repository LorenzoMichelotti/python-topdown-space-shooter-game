import pygame


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}

    def load_sound(self, name: str, filepath: str, volume: float = 0.2):
        sound = pygame.mixer.Sound(filepath)
        sound.set_volume(volume)
        self.sounds[name] = sound

    def play_sound(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()
