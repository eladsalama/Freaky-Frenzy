import pygame
import math
import random

from effect import Effect
from Enemies.enemy import Enemy
from pickup import Pickup


class MiniBoss(Enemy):
    def __init__(self, pos, miniboss_type, player_lvl):
        super().__init__(pos, miniboss_type, player_lvl)

    def take_dmg(self, game, dmg):
        self.health -= dmg
        if self.health <= 0:
            if self in game.mini_bosses:
                game.mini_bosses.remove(self)

            game.effects.append(Effect(self.pos, 0, self.size * 7, self.color, 0.12, "ripple"))
            game.player.exp += game.player.exp_to_level
            game.score += 1000
            game.player.exp += game.player.exp_to_level - game.player.exp
            Pickup.drop(self, game.pickups)

    @staticmethod
    def draw_screen_glow(game):
        # Updated glow effect
        glow_intensity = 0.4 + 0.1 * math.sin(pygame.time.get_ticks() / 400)
        glow_color = (int(33 * glow_intensity), int(15 * glow_intensity), int(33 * glow_intensity), 100)

        # Draw the glow
        glow_surface = pygame.Surface((game.WIDTH, game.HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (game.WIDTH // 2, game.HEIGHT // 2), game.WIDTH)
        game.screen.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)