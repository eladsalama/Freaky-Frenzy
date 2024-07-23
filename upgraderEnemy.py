import math
import pygame

from enemy import Enemy
from effect import Effect


class UpgraderEnemy(Enemy):
    upgrade_radius = 150

    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)

        if enemy_type == "upgrader":
            self.speed *= 2
            self.damage = 0
            self.size = 12
            self.exp_value = 100
            self.color = Enemy.upgrader_color

            self.upgraded_enemies = []

    def move(self, game, avoid_radius=200):
        super().move(game, avoid_radius)

    def upgrade_enemies(self, game):
        if len(self.upgraded_enemies) < 4:
            for enemy in game.enemies:
                if (enemy.enemy_type != "upgrader" and not enemy.upgraded and
                        math.hypot(self.pos[0] - enemy.pos[0],
                                   self.pos[1] - enemy.pos[1]) < UpgraderEnemy.upgrade_radius):
                    self.upgraded_enemies.append(enemy)
                    enemy.upgrade()
                    enemy.upgrader = self
                    break

    def draw(self, screen):
        points = []
        for i in range(6):
            radius = self.size
            if i in [1,2,4,5]:
                radius *= 0.7

            points.append((self.pos[0] + radius * math.sin(i * 2 * math.pi / 6), self.pos[1] + radius * math.cos(i * 2 * math.pi / 6)))

        pygame.draw.polygon(screen, self.color, points)

        for enemy in self.upgraded_enemies:
            pygame.draw.line(screen, self.color, self.pos, enemy.pos, 2)