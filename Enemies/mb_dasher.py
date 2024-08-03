import pygame
import math
import random

from Enemies.miniBoss import MiniBoss
from effect import Effect
from Enemies.enemy import Enemy
from pickup import Pickup


class MB_Dasher(MiniBoss):
    def __init__(self, pos, miniboss_type, player_lvl):
        super().__init__(pos, miniboss_type, player_lvl)

        self.size = 50
        self.max_health = 500 * 7 ** (player_lvl % 5)
        self.health = self.max_health
        self.damage = 1
        self.speed = 1

        self.exp_value = 10
        self.color = (0, 255, 255)
        self.original_color = self.color

        self.dash_count = 0
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_direction = [0, 0]
        self.spike_rotation_angle = 0

    def move(self, game):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        else:
            self.dash(game)

    def dash(self, game):
        if self.dash_duration > 0:
            # dash
            dash_speed = self.max_speed * 10
            self.pos[0] += self.dash_direction[0] * dash_speed
            self.pos[1] += self.dash_direction[1] * dash_speed
            self.dash_duration -= 1
            return

        if self.dash_count < 3:
            # start dash
            self.dash_count += 1
            self.dash_duration = 10 + 5 * self.dash_count

            dx = game.player.pos[0] - self.pos[0]
            dy = game.player.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)

            if self.dash_count < 3:
                # For the first two dashes, add some randomness to the direction
                dash_noise = self.dash_count + 2
                angle = math.atan2(dy, dx) + random.uniform(-math.pi / dash_noise, math.pi / dash_noise)
                self.dash_direction = [math.cos(angle), math.sin(angle)]
            else:
                # For the third dash, aim directly at the player
                self.dash_direction = [dx / dist, dy / dist] if dist != 0 else [0, 0]
        else:
            # reset dash
            self.dash_count = 0
            self.dash_cooldown = 150

    def draw(self, screen):
        self.draw_hp_bar(screen)

        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), int(self.size * 0.25))
        arc_radius = self.size * 0.6
        pygame.draw.arc(screen, self.color,
                        (int(self.pos[0] - arc_radius), int(self.pos[1] - arc_radius), int(arc_radius * 2), int(arc_radius * 2)),
                        0, 2 * math.pi, width=6)

        # Update rotation angle
        if self.dash_duration > 0:
            num_spikes = 5
            self.spike_rotation_angle += 30  # fast rotation when dashing
        else:
            num_spikes = 9
            self.spike_rotation_angle += 1  # slow rotation
        self.spike_rotation_angle %= 360

        angle_increment = 360 / num_spikes

        for i in range(num_spikes):
            angle = math.radians(angle_increment * i + self.spike_rotation_angle)
            next_angle = math.radians(angle_increment * (i + 1) + self.spike_rotation_angle)

            x1 = self.pos[0] + arc_radius * math.cos(angle)
            y1 = self.pos[1] + arc_radius * math.sin(angle)

            x2 = self.pos[0] + arc_radius * math.cos(next_angle - math.pi / 10)
            y2 = self.pos[1] + arc_radius * math.sin(next_angle - math.pi / 10)

            x3 = self.pos[0] + self.size * math.cos(next_angle)
            y3 = self.pos[1] + self.size * math.sin(next_angle)

            pygame.draw.polygon(screen, (192, 192, 192), [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])
