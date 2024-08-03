import pygame
import math

from Enemies.enemy import Enemy
from Projectiles.projectile import Projectile


class Archer(Enemy):
    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)

        self.speed *= 1.2
        self.max_speed = self.speed
        self.avoid_radius = 200
        self.damage *= 0.5
        self.size = 15
        self.exp_value = 20
        self.color = (255, 215, 0)
        self.original_color = self.color
        self.angle = 0
        self.shooting = True
        self.shoot_timer = 0
        self.shoot_interval = 60

        self.bullet_dmg = 3
        self.bullet_size = 3
        self.bullet_shape = "circle"
        self.bullet_color = (255, 255, 0)

    def shoot(self, game):
        self.angle = math.atan2(game.player.pos[1] - self.pos[1], game.player.pos[0] - self.pos[0])

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            game.enemy_projectiles.append(Projectile(self.pos, self.angle, 10, self.bullet_shape, self.bullet_color,
                                          self.bullet_size, self.bullet_dmg, self))

    def upgrade_lightning(self, revert):
        if not revert:
            self.speed *= 2
            self.shoot_interval = 20
            self.bullet_dmg = 5
            self.bullet_size = 5
            self.bullet_color = self.upgrader.color

        else:
            self.speed /= 2
            self.shoot_interval = 60
            self.bullet_dmg = 3
            self.bullet_size = 3
            self.bullet_color = self.bullet_color

    def move(self, game, avoid_radius=0):
        super().move(game, avoid_radius=self.avoid_radius)

    def draw(self, screen):
        if self.upgraded:
            self.draw_archer(screen, self.size * 1.85, self.upgrader.color, True)
        self.draw_archer(screen, self.size * 1.3, (125, 83, 0), True)
        self.draw_archer(screen, self.size * 1.3, self.color, False)

    def draw_archer(self, screen, radius, color, fill):
        x1 = self.pos[0] + radius * math.cos(self.angle)
        y1 = self.pos[1] + radius * math.sin(self.angle)

        x2 = self.pos[0] - radius * math.cos(self.angle + math.pi / 4)
        y2 = self.pos[1] - radius * math.sin(self.angle + math.pi / 4)

        x3 = self.pos[0] - radius * 0.2 * math.cos(self.angle)
        y3 = self.pos[1] - radius * 0.2 * math.sin(self.angle)

        x4 = self.pos[0] - radius * math.cos(self.angle - math.pi / 4)
        y4 = self.pos[1] - radius * math.sin(self.angle - math.pi / 4)

        if fill:
            pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
        else:
            pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)], 3)