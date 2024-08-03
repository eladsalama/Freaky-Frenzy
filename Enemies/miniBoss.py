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

    def draw_screen_glow(self, screen):
        # Updated glow effect
        glow_radius = self.size * 20
        glow_intensity = 0.4 + 0.1 * math.sin(pygame.time.get_ticks() / 400)
        glow_color = (int(33 * glow_intensity), int(15 * glow_intensity), int(33 * glow_intensity), 100)

        # Draw the glow
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_rect_center = (glow_radius, glow_radius)
        pygame.draw.circle(glow_surface, glow_color, glow_rect_center, glow_radius)
        screen.blit(glow_surface, (self.pos[0] - glow_radius, self.pos[1] - glow_radius),
                    special_flags=pygame.BLEND_ADD)