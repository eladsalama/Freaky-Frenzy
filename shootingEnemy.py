import pygame
import math

from enemy import Enemy
from projectile import Projectile


class ShootingEnemy(Enemy):
    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)
        self.angle = 0

        self.shooting = True
        self.shoot_timer = 0
        self.shoot_interval = 60

        self.bullet_dmg = 3

        self.bullet_color = (255, 255, 0)
        self.bullet_size = 3

        if enemy_type == "archer":
            self.speed *= 1.2
            self.damage = 5
            self.size = 15
            self.exp_value = 20
            self.color = (255, 215, 0)

    def upgrade(self, revert=False):
        super().upgrade(revert)
        if not revert:
            self.shoot_interval /= 2
            self.bullet_dmg *= 3
            self.bullet_size *= 3
            self.bullet_color = Enemy.upgrader_color
        else:
            self.shoot_interval *= 2
            self.bullet_dmg //= 3
            self.bullet_size /= 3
            self.bullet_color = self.bullet_color

    def shoot(self, player, projectiles):
        self.angle = math.atan2(player.pos[1] - self.pos[1], player.pos[0] - self.pos[0])

        if self.enemy_type == "archer":
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0
                projectiles.append(Projectile(self.pos[0], self.pos[1], self.angle, self.bullet_color,
                                              self.bullet_size, self.bullet_dmg, 1))

    def move(self, game, avoid_radius=0):
        if self.enemy_type == "archer":
            super().move(game, avoid_radius=200)

    def draw(self, screen):
        if self.upgraded:
            self.draw_archer(screen, self.size * 1.7, Enemy.upgrader_color)
        self.draw_archer(screen, self.size * 1.3, self.color)

    def draw_archer(self, screen, radius, color):
        x1 = self.pos[0] + radius * math.cos(self.angle)
        y1 = self.pos[1] + radius * math.sin(self.angle)

        x2 = self.pos[0] - radius * math.cos(self.angle + math.pi / 4)
        y2 = self.pos[1] - radius * math.sin(self.angle + math.pi / 4)

        x3 = self.pos[0] - radius * 0.2 * math.cos(self.angle)
        y3 = self.pos[1] - radius * 0.2 * math.sin(self.angle)

        x4 = self.pos[0] - radius * math.cos(self.angle - math.pi / 4)
        y4 = self.pos[1] - radius * math.sin(self.angle - math.pi / 4)

        pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])