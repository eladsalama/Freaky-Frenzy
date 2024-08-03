import pygame

import math
import numpy as np

import general


class Projectile:
    def __init__(self, pos, angle, speed, shape, color, size, dmg, shooter, proj_type='normal', target=None):
        self.pos = pos[:]
        self.angle = angle
        self.velocity = np.array([math.cos(angle) * speed, math.sin(angle) * speed], dtype=np.float64)

        self.proj_type = proj_type
        self.speed = speed
        self.color = color
        self.shape = shape
        self.size = size
        self.shooter = shooter

        self.dmg = dmg
        self.pierce = 0

        self.target = target

    def update_homing_projectile(self, game, new_pos):
        if self.target and self.target.health > 0:
            target_pos = np.array(self.target.pos)
            direction = target_pos - new_pos
            target_angle = math.atan2(direction[1], direction[0])

            angle_difference = target_angle - self.angle
            angle_difference = (angle_difference + math.pi) % (2 * math.pi) - math.pi

            turning_speed = 0.1
            if abs(angle_difference) < turning_speed:
                self.angle = target_angle
            else:
                self.angle += turning_speed if angle_difference > 0 else -turning_speed

            self.velocity = np.array([math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed])

        else:
            target = general.get_closest(game.player.pos, game.enemies + game.mini_bosses)
            if target:
                self.target = target[0]

        self.pos = new_pos

    def draw(self, screen):
        if self.shape == "circle":
            pygame.draw.circle(screen, self.color, self.pos, self.size)
        elif self.shape == "line":
            start_pos = (int(self.pos[0] - math.cos(self.angle) * 20),
                       int(self.pos[1] - math.sin(self.angle) * 20))
            end_pos = (int(self.pos[0] + math.cos(self.angle) * 20),
                       int(self.pos[1] + math.sin(self.angle) * 20))
            pygame.draw.line(screen, self.color, start_pos, end_pos, int(self.size * 1.5))
            pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, int(self.size * 0.7))
