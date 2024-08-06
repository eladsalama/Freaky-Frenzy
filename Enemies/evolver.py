import math
import pygame

from Enemies.enemy import Enemy


class Evolver(Enemy):
    upgrade_radius = 200

    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos, enemy_type, player_lvl)

        self.damage = 0
        self.size = 15
        self.exp_value = 100

        self.upgraded_enemies = []
        self.upgrade_amount = 3

        if enemy_type == "upg_lightning":
            self.color = (138, 43, 226)

        if enemy_type == "upg_frost":
            self.color = (0, 220, 220)

        if enemy_type == "upg_fire":
            self.color = (255, 69, 0)

        self.original_color = self.color

    def move(self, game, avoid_radius=350):
        super().move(game, avoid_radius)

    def upgrade_enemies(self, game):
        if len(self.upgraded_enemies) < self.upgrade_amount:
            for enemy in game.enemies:
                if (not isinstance(enemy, Evolver) and not enemy.upgraded and
                        math.hypot(self.pos[0] - enemy.pos[0],
                                   self.pos[1] - enemy.pos[1]) < Evolver.upgrade_radius):
                    self.upgraded_enemies.append(enemy)
                    enemy.upgrader = self
                    enemy.upgrade(self.enemy_type, False)

                    break

    def draw(self, screen):
        points = []
        for i in range(6):
            radius = self.size
            if i in [1, 2, 4, 5]:
                radius *= 0.7

            points.append((self.pos[0] + radius * math.sin(i * 2 * math.pi / 6), self.pos[1] + radius * math.cos(i * 2 * math.pi / 6)))

        pygame.draw.polygon(screen, self.color, points, 4)

        for enemy in self.upgraded_enemies:
            pygame.draw.line(screen, self.color, self.pos, enemy.pos, 2)