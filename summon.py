import pygame
import math
import random
from pickup import Pickup


class Summon:
    def __init__(self, pos, angle, summon_type):
        self.pos = pos
        self.angle = angle
        self.summon_type = summon_type

        # Set attributes based on type
        if summon_type == "spinning_sword":
            self.damage = 1
            self.speed = 1
            self.size = 5

        elif summon_type == "healer":
            self.damage = 0
            self.speed = 1
            self.size = 5

    def move(self, game):
        if self.summon_type == "spinning_sword":
            self.move_spinning_swords(game)
        if self.summon_type == "healer":
            self.move_healer(game)

    def move_spinning_swords(self, game):
        self.angle += (math.pi / 180)
        self.angle = self.angle % (2 * math.pi)
        self.pos[0] = game.player.pos[0] + 70 * math.cos(self.angle)
        self.pos[1] = game.player.pos[1] + 70 * math.sin(self.angle)

    def move_healer(self, game):
        dx = game.player.pos[0] - self.pos[0]
        dy = game.player.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)

        if dist > 50:
            dx, dy = dx / dist, dy / dist  # Normalize

            self.pos[0] += dx * self.speed
            self.pos[1] += dy * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255,255,255), (int(self.pos[0]), int(self.pos[1])), self.size)
