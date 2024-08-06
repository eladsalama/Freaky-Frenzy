import pygame
import random
import math


class Pickup:
    drop_chances = {'health': 0.025, 'ammo': 0.005, 'exp': 0.15, 'nuke': 0.0005, 'freeze': 0.001}
    ammo_upgrade_bonus = 0

    def __init__(self, x, y, pickup_type):
        self.x = x
        self.y = y
        self.type = pickup_type
        self.speed = 3
        self.size = 5
        self.spawn_time = pygame.time.get_ticks()

        if self.type == 'omnivamp_health':
            self.speed = 20
            self.size = 3

    @staticmethod
    def apply_pickup(game, drop_type):
        if drop_type == 'health':
            game.player.health = min(game.player.health + random.randint(10, 25), game.player.max_health)
        if drop_type == 'omnivamp_health':
            game.player.health = min(game.player.max_health, game.player.health + game.player.omnivamp_lvl * 5)
        elif drop_type == 'ammo':
            game.player.ammo += 15 + Pickup.ammo_upgrade_bonus
        elif drop_type == 'exp':
            game.player.exp += int(random.randint(10, 30) * 1.5 ** game.player.lvl % 10)
        elif drop_type == 'nuke':
            game.score += len(game.enemies) * 10
            game.player.exp += len(game.enemies) * 10
            game.enemies = []
            game.shooting_enemies = []
        elif drop_type == 'freeze':
            if not game.freeze:
                game.player.fire_rate /= 5
            game.freeze = True
            game.freeze_time = pygame.time.get_ticks()

    @staticmethod
    def drop(enemy, pickups, specific_drop=None):
        if specific_drop:
            pickups.append(Pickup(enemy.pos[0], enemy.pos[1], specific_drop))
        else:
            for pickup_type, chance in Pickup.drop_chances.items():
                if enemy.enemy_type == "archer" and pickup_type == "ammo" or random.random() < chance:
                    pickups.append(Pickup(enemy.pos[0], enemy.pos[1], pickup_type))

    def move(self, player):
        pickup_range = 0
        lvl_increment = 1

        if self.type == 'omnivamp_health':
            pickup_range = 9999

        elif player.magnet_lvl > 0:
            lvl_increment = player.magnet_lvl * 2
            pickup_range = 65 * lvl_increment

        if pickup_range > 0:
            dx = player.pos[0] - self.x
            dy = player.pos[1] - self.y
            dist = math.hypot(dx, dy)

            if dist < pickup_range:
                self.x += dx / dist * (self.speed * lvl_increment)
                self.y += dy / dist * (self.speed * lvl_increment)

    def draw(self, screen):
        colors = {'health': (220, 20, 60), 'omnivamp_health': (220, 20, 60),
                  'ammo': (255, 215, 0), 'exp': (147, 112, 219), 'nuke': (255, 255, 255),
                  'freeze': (0, 255, 255)}
        pygame.draw.circle(screen, colors[self.type], (int(self.x), int(self.y)), self.size)
