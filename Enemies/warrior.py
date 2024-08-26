import pygame
import math
import random

from Enemies.enemy import Enemy
from pickup import Pickup


class Warrior(Enemy):
    upgrader_color = (138, 43, 226)

    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)

        self.size = 12
        self.speed *= 1.5
        self.max_speed = self.speed
        self.exp_value = 1
        #self.color = (255, 27, 51)
        #self.original_color = self.color

    def upgrade_lightning(self, revert):
        if not revert:
            self.health *= 1.5
            self.damage *= 2
            self.speed *= 1.5

        else:
            self.health /= 1.5
            self.damage //= 2
            self.speed /= 1.5

    def draw(self, screen):
        color = self.upgrader.color if self.upgraded else self.color_secondary

        if self.upgraded:
            pygame.draw.circle(screen, self.upgrader.color, (int(self.pos[0]), int(self.pos[1])), self.size + 5)

        pygame.draw.circle(screen, color, (int(self.pos[0]), int(self.pos[1])), self.size)
        pygame.draw.arc(screen, self.color,
                        (int(self.pos[0]) - self.size, int(self.pos[1]) - self.size, self.size * 2, self.size * 2),
                        0, 2 * math.pi, width=2)
