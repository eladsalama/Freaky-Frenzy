import pygame
import math
import random

class Effect:
    def __init__(self, pos, size, color, duration, effect_type):
        self.x, self.y = pos[0], pos[1]
        self.size = size
        self.color = color
        self.effect_type = effect_type

        self.duration = duration * 1000
        self.time_start = pygame.time.get_ticks()
        self.time_end = self.time_start + self.duration

    def draw(self, screen):
        if self.effect_type == "ripple":
            self.draw_ripple(screen)

    def draw_ripple(self, screen):
        radius = (pygame.time.get_ticks() - self.time_start) / self.duration * (self.size / 2)
        pygame.draw.arc(screen, self.color,(self.x - radius, self.y - radius, radius * 2, radius * 2),
                        0, 2 * math.pi, width=3)
