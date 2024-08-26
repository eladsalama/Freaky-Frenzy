import math

import pygame
from Enemies.enemy import Enemy
from Projectiles.projectile import Projectile


class Tank(Enemy):
    upgrader_color = (138, 43, 226)

    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)

        self.health *= 3
        self.damage *= 3
        self.speed *= 0.75
        self.max_speed = self.speed
        self.size = 19
        self.exp_value = 3
        self.original_color = self.color

        self.shooting = True
        self.shoot_timer = 0
        self.shoot_intervals = [250, 250]
        self.shoot_intervals_index = 0

        self.bullet_dmg = 8
        self.bullet_size = 7
        self.bullet_shape = "circle"
        #self.bullet_color = (120, 120, 120)

    def shoot(self, game):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_intervals[self.shoot_intervals_index]:
            self.shoot_intervals_index = (self.shoot_intervals_index + 1) % len(self.shoot_intervals)
            self.shoot_timer = 0

            for i in range(4):
                self.create_bullet(game, math.pi / 2 * i + math.pi / 4 * self.shoot_intervals_index)

    def create_bullet(self, game, angle):
        game.enemy_projectiles.append(Projectile(self.pos, angle, 6, self.bullet_shape, self.bullet_color,
                                                 self.bullet_size, self.bullet_dmg, self))

    def upgrade_lightning(self, revert):
        if not revert:
            self.health *= 2
        else:
            self.health //= 2

    def draw(self, screen):
        color = self.upgrader.color if self.upgraded else self.color_secondary
        length = 45
        if self.upgraded:
            pygame.draw.rect(screen, self.upgrader.color,
                             pygame.Rect((int(self.pos[0]) - length // 2 - 4, int(self.pos[1]) - length // 2 - 4,
                                          length + 8, length + 8)))

        pygame.draw.rect(screen, color,
                         pygame.Rect((int(self.pos[0]) - length // 2, int(self.pos[1]) - length // 2, length, length)))

        pygame.draw.rect(screen, self.color,
                         pygame.Rect((int(self.pos[0]) - length // 2, int(self.pos[1]) - length // 2, length, length)), 4)