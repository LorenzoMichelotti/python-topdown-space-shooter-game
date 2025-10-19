# Example file showing a basic pygame "game loop"
import pygame

from entities.cursor import Cursor
from entities.enemy import Enemy
from entities.player import Player
from scenes.scene import Scene
from systems.camera import Camera
from systems.entity_manager import EntityManager
from systems.sound_manager import SoundManager
from systems.wave_manager import WaveManager
from ui.level_hud import LevelHud


class Level(Scene):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.camera = Camera(screen)
        self.game_over = False
        self.game_over_timer = 0  # Delay before showing restart message

        # load entities
        self.player = Player(screen)
        self.enemy = Enemy(
            screen,
            pygame.Vector2(screen.get_width() / 2 - 200, screen.get_height() / 2),
        )
        self.sound_manager = SoundManager()
        self.entity_manager = EntityManager(sound_manager=self.sound_manager)
        self.entity_manager.camera = self.camera  # Give entity manager access to camera
        self.wave_manager = WaveManager(
            entity_manager=self.entity_manager, screen=screen
        )
        self.cursor = Cursor(screen)
        self.hud = LevelHud()

    def setup(self):
        pygame.mouse.set_visible(False)
        # entity_manager.instantiate(enemy)
        self.sound_manager.load_sound("shoot", "assets/sounds/Shoot6.wav", 0.1)
        self.sound_manager.load_sound("explosion", "assets/sounds/Boom10.wav")
        self.sound_manager.load_sound("hit", "assets/sounds/Hit.wav")

        self.entity_manager.instantiate(self.player)
        self.entity_manager.instantiate(self.cursor)

        self.wave_manager.start_next_wave()

    def restart(self):
        """Restart the game"""
        self.game_over = False
        self.game_over_timer = 0
        self.entity_manager.score = 0

        # Clear all entities
        self.entity_manager.entities.clear()

        # Recreate player and cursor
        self.player = Player(self.screen)
        self.cursor = Cursor(self.screen)

        # Re-instantiate them
        self.entity_manager.instantiate(self.player)
        self.entity_manager.instantiate(self.cursor)

        # Restart wave system
        self.wave_manager.current_wave_index = 0
        self.wave_manager.wave_in_progress = False
        self.wave_manager.enemies_spawned = 0
        self.wave_manager.time_since_last_spawn = 0.0
        self.wave_manager.start_next_wave()

    def render(self, dt: float):
        # Check if player is dead
        if not self.game_over and self.player.hp <= 0:
            self.game_over = True
            self.game_over_timer = 0

        # Handle restart input
        if self.game_over:
            self.game_over_timer += dt
            keys = pygame.key.get_pressed()
            if (
                keys[pygame.K_r] and self.game_over_timer > 1.0
            ):  # Wait 1 second before allowing restart
                self.restart()
                return

        # Update camera shake
        self.camera.update(dt)

        # Get camera offset
        offset = self.camera.get_offset()

        # Create a surface for the world (with camera offset)
        world_surface = pygame.Surface(self.screen.get_size())
        world_surface.fill("blue")

        # Temporarily replace screen with world surface for entities to draw on
        original_screen = self.screen
        for entity in self.entity_manager.entities:
            entity.screen = world_surface

        # Update entities (they draw to world_surface)
        # Note: Cursor will be drawn separately later to appear on top of overlays
        self.entity_manager.update(dt)
        self.wave_manager.update(dt)

        # Restore original screen
        for entity in self.entity_manager.entities:
            entity.screen = original_screen

        # Draw world surface to screen with camera offset
        self.screen.blit(world_surface, offset)

        # Draw game over screen
        if self.game_over:
            # Semi-transparent dark overlay
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # Game over text
            font_large = pygame.font.Font(None, 74)
            font_small = pygame.font.Font(None, 36)

            game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
            game_over_rect = game_over_text.get_rect(
                center=(self.screen.get_width() / 2, self.screen.get_height() / 2 - 50)
            )
            self.screen.blit(game_over_text, game_over_rect)

            # Show restart message after delay
            if self.game_over_timer > 1.0:
                restart_text = font_small.render(
                    "Press R to Restart", True, (255, 255, 255)
                )
                restart_rect = restart_text.get_rect(
                    center=(
                        self.screen.get_width() / 2,
                        self.screen.get_height() / 2 + 50,
                    )
                )
                self.screen.blit(restart_text, restart_rect)

        # Draw pause screen
        if self.entity_manager.paused:
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            font_large = pygame.font.Font(None, 74)
            font_small = pygame.font.Font(None, 36)

            pause_text = font_large.render("PAUSED", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(
                center=(self.screen.get_width() / 2, self.screen.get_height() / 2 - 50)
            )
            self.screen.blit(pause_text, pause_rect)

            resume_text = font_small.render("esc to resume", True, (255, 255, 255))
            resume_rect = resume_text.get_rect(
                center=(
                    self.screen.get_width() / 2,
                    self.screen.get_height() / 2 + 10,
                )
            )
            self.screen.blit(resume_text, resume_rect)

        # Draw cursor on top of everything (overlays, HUD, etc.)
        self.cursor.draw_shadow()
        self.cursor.draw()

        self.hud.render(self.screen, dt, self.player, self.wave_manager)
        pygame.display.flip()
