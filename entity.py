import math
import random
import pygame


class Entity:
    def __init__(self, pos):
        self.pos = pos
        self.angle = math.pi / 2
        self.velocity_angle = self.angle

        self.size = 10

        self.health = 100
        self.max_health = self.health

        self.speed = 0
        self.max_speed = 2

        self.color = (255, 0, 0)
        self.original_color = self.color

    def take_dmg(self, dmg):
        self.health -= dmg

    def update(self, game):
        return

    def draw_hp_bar(self, screen):
        # draw hp bar
        hp_bar_width = self.size * 1.2
        hp_bar_height = 5
        hp_bar_x = int(self.pos[0] - hp_bar_width / 2)
        hp_bar_y = int(self.pos[1] - self.size - hp_bar_height - 15)  # 15 pixels above the miniboss

        # Background of HP bar (dark gray)
        pygame.draw.rect(screen, (120, 120, 120), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))

        # Foreground of HP bar (red)
        health_percentage = self.health / self.max_health
        current_hp_width = int(hp_bar_width * health_percentage)
        pygame.draw.rect(screen, (255, 0, 0), (hp_bar_x, hp_bar_y, current_hp_width, hp_bar_height))