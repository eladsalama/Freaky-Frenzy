import math

import pygame


class Projectile:
    def __init__(self, x, y, angle, color, size, dmg, shooter_type, proj_type='normal', destructible=True):
        self.x = x
        self.y = y
        self.angle = angle

        self.proj_type = proj_type
        self.speed = 10
        self.color = color
        self.size = size
        self.shooter_type = shooter_type

        self.dmg = dmg
        self.pierce = 0

        self.destructible = destructible

    def move(self, game):
        if self.proj_type == "normal":
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

            if self.x < 0 or self.x > game.WIDTH or self.y < 0 or self.y > game.HEIGHT:
                if self.shooter_type == 0:
                    game.player_projectiles.remove(self)
                else:
                    game.enemy_projectiles.remove(self)

    def draw(self, screen):
        if self.proj_type == "normal":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
