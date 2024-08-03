import pygame
import math
import random
import numpy as np

class Effect:
    def __init__(self, pos, angle, size, color, duration, effect_type):
        self.pos = pos
        self.angle = angle
        self.size = size
        self.color = color
        self.effect_type = effect_type

        self.duration = duration * 1000
        self.time_start = pygame.time.get_ticks()
        self.time_end = self.time_start + self.duration

        if self.effect_type == "dot_splatter":
            self.dots = self.init_dot_splatter()

    def draw(self, screen):
        if self.effect_type == "ripple":
            self.ripple(screen)
        if self.effect_type == "jagged_line":
            self.jagged_line(screen)
        if self.effect_type == "dot_splatter":
            self.dot_splatter(screen)
        if self.effect_type == "arrow_up":
            self.arrow_up(screen)

    def ripple(self, screen):
        center = self.pos
        radius = (pygame.time.get_ticks() - self.time_start) / self.duration * (self.size / 2)
        pygame.draw.arc(screen, self.color,(center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                        0, 2 * math.pi, width=3)

    def jagged_line(self, screen):
        start = self.pos[0]
        end = self.pos[1]
        points = [start]
        dx, dy = end[0] - start[0], end[1] - start[1]
        steps = int(math.hypot(dx, dy) / 10)

        for i in range(1, steps):
            t = i / steps
            x = start[0] + dx * t + random.uniform(-5, 5)
            y = start[1] + dy * t + random.uniform(-5, 5)
            points.append((x, y))

        points.append(end)

        # Draw the jagged line
        pygame.draw.lines(screen, self.color, False, points, self.size)

    def init_dot_splatter(self):
        amount = random.randint(3, 8)
        dots = [(self.pos[:], random.randrange(5,10), self.angle + random.uniform(-math.pi / 12, math.pi / 12))
                for i in range(amount)]
        dtypes = [('pos', float, 2), ('speed', float), ('angle', float)]
        return np.array(dots, dtype=dtypes)

    def dot_splatter(self, screen):
        self.dots['pos'] += np.column_stack((np.cos(self.dots['angle']), np.sin(self.dots['angle']))) * self.dots['speed'][:,np.newaxis]
        self.dots['speed'] *= 0.95

        for dot_pos in self.dots['pos']:
            pygame.draw.circle(screen, self.color, dot_pos, self.size)

    def arrow_up(self, screen):
        width = self.size
        height = self.size * 1.3
        points = np.array([(width // 2, 0),
                          (0, height // 2),
                          (width // 4, height // 2),
                          (width // 4, height),
                          (3 * width // 4, height),
                          (3 * width // 4, height // 2),
                          (width, height // 2)], dtype=float) + np.array(self.pos) + np.array([15,-15])
        points[:, 1] -= (pygame.time.get_ticks() - self.time_start) / self.duration * 25
        pygame.draw.polygon(screen, self.color, points)





