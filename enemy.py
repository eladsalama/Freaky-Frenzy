import pygame
import math
import random
from pickup import Pickup


class Enemy:
    upgrader_color = (138, 43, 226)

    def __init__(self, pos, enemy_type, player_lvl):
        self.pos = pos

        self.enemy_type = enemy_type
        self.color = (0, 255, 0)  # Default to green

        self.health = 1 + 0.5 * player_lvl // 10
        self.speed = 2 + 0.5 * player_lvl // 15

        self.shooting = False

        self.upgraded = False
        self.upgrader = None

        # Set attributes based on type
        if enemy_type == "normal":
            self.damage = 10
            self.size = 15
            self.exp_value = 10
            self.color = (0, 255, 0)  # Green
        elif enemy_type == "tank":
            self.health *= 3
            self.speed *= 0.75
            self.damage = 30
            self.size = 19
            self.exp_value = 30
            self.color = (128, 128, 128)  # Gray

    def take_dmg(self, game, dmg):
        self.health -= dmg
        if self.health <= 0:
            if self in game.enemies:
                game.enemies.remove(self)

            if game.player.omnivamp_lvl > 0 and random.random() < 0.25:
                Pickup.drop(self, game.pickups, 'omnivamp_health')

            # upgrade
            if self.upgraded and self in self.upgrader.upgraded_enemies:
                self.upgrader.upgraded_enemies.remove(self)
            if self.enemy_type == "upgrader":
                for enemy in self.upgraded_enemies:
                    enemy.upgrade(revert=True)

            # reward
            game.score += 10
            game.player.exp += self.exp_value
            Pickup.drop(self, game.pickups)

    def move(self, game, avoid_radius=0):
        dx = game.player.pos[0] - self.pos[0]
        dy = game.player.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist != 0:
            dx, dy = dx / dist, dy / dist  # Normalize

        direction = 0
        if dist >= avoid_radius:
            direction = 1
        elif dist <= avoid_radius * 0.9:
            direction = -1
        else:
            return

        new_x = self.pos[0] + direction * dx * self.speed
        new_y = self.pos[1] + direction * dy * self.speed

        self.correct_overlap(new_x, new_y, game.enemies)

    def correct_overlap(self, new_x, new_y, enemies):
        for enemy in enemies:
            if enemy != self:
                distance = math.hypot(new_x - enemy.pos[0], new_y - enemy.pos[1])
                if distance < self.size + enemy.size:
                    # Adjust movement to avoid overlap
                    angle = math.atan2(new_y - enemy.pos[1], new_x - enemy.pos[0])
                    new_x = enemy.pos[0] + math.cos(angle) * (self.size + enemy.size)
                    new_y = enemy.pos[1] + math.sin(angle) * (self.size + enemy.size)

        self.pos[0] = new_x
        self.pos[1] = new_y

    def upgrade(self, revert=False):
        if not revert:
            self.upgraded = True
            self.health *= 1.5
            self.damage *= 2
            self.speed *= 2
            self.exp_value *= 2

            if self.enemy_type == 'tank':
                self.health *= 2
        else:
            self.upgraded = False
            self.health /= 1.5
            self.damage //= 2
            self.speed /= 2
            self.exp_value //= 2

            if self.enemy_type == 'tank':
                self.health //= 2

    def draw(self, screen):
        if self.enemy_type in ['normal', 'archer', 'upgrader']:
            if self.upgraded:
                pygame.draw.circle(screen, Enemy.upgrader_color, (int(self.pos[0]), int(self.pos[1])), self.size + 4)
            pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.size)

        if self.enemy_type == 'tank':
            length = 45
            if self.upgraded:
                pygame.draw.rect(screen, Enemy.upgrader_color,
                                 pygame.Rect((int(self.pos[0]) - length // 2 - 4, int(self.pos[1]) - length // 2 - 4,
                                              length + 8, length + 8)))
            pygame.draw.rect(screen, self.color,
                             pygame.Rect(
                                 (int(self.pos[0]) - length // 2, int(self.pos[1]) - length // 2, length, length)))
