import math

import pygame
from Enemies.enemy import Enemy


class Tank(Enemy):
    upgrader_color = (138, 43, 226)

    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)

        self.health *= 3
        self.damage *= 3
        self.speed *= 0.75
        self.max_speed = self.speed
        self.size = 19
        self.exp_value = 30
        self.color = (128, 128, 128)
        self.original_color = self.color

    def upgrade_lightning(self, revert):
        if not revert:
            self.health *= 2
        else:
            self.health //= 2

    def draw(self, screen):
        length = 45
        if self.upgraded:
            pygame.draw.rect(screen, self.upgrader.color,
                             pygame.Rect((int(self.pos[0]) - length // 2 - 4, int(self.pos[1]) - length // 2 - 4,
                                          length + 8, length + 8)))

        pygame.draw.rect(screen, (70, 70, 70),
                         pygame.Rect((int(self.pos[0]) - length // 2, int(self.pos[1]) - length // 2, length, length)))

        pygame.draw.rect(screen, self.color,
                         pygame.Rect((int(self.pos[0]) - length // 2, int(self.pos[1]) - length // 2, length, length)), 4)