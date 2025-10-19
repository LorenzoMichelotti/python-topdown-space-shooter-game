import pygame


class LevelHud:
    def render(self, screen: pygame.Surface, dt: float, player, wave_manager):
        health_bar_width = 200
        health_bar_height = 40
        health_ratio = player.hp / player.max_hp

        # health bar shadow
        shadow_rect = pygame.Rect(10, 20, health_bar_width, health_bar_height)
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect)
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            pygame.Rect(10, 20, health_bar_width, health_bar_height),
            5,
        )

        # health bar background
        background_rect = pygame.Rect(10, 10, health_bar_width, health_bar_height)
        pygame.draw.rect(screen, (50, 50, 70), background_rect)

        # Render health bar
        health_bar_rect = pygame.Rect(
            10, 10, health_bar_width * health_ratio, health_bar_height
        )
        pygame.draw.rect(screen, (0, 255, 0), health_bar_rect)
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            pygame.Rect(10, 10, health_bar_width, health_bar_height),
            5,
        )

        # render current wave
        font = pygame.font.Font(None, 36)
        wave_text = font.render(
            f"Wave: {wave_manager.current_wave_index}",
            True,
            (
                255,
                255,
                255,
            ),
        )
        screen.blit(wave_text, (screen.get_width() - 150, 10))

        # render current score
        score_text = font.render(
            f"Score: {player.entity_manager.score}", True, (255, 255, 255)
        )
        screen.blit(score_text, (screen.get_width() - 150, 50))
