import pygame
import math
import random

from effect import Effect
from enemy import Enemy
from pickup import Pickup


class MiniBoss(Enemy):
    def __init__(self, pos, miniboss_type, player_lvl):
        super().__init__(pos, miniboss_type, player_lvl)
        self.pos = pos

        self.enemy_type = miniboss_type

        if miniboss_type == 'normal_mb':
            self.size = 50
            self.max_health = 100 * 1.5 ** (player_lvl % 10)
            self.health = self.max_health
            self.damage = 1
            self.speed = 1

            self.exp_value = 10
            self.color = (0, 255, 255)

            self.dash_count = 0
            self.dash_cooldown = 0
            self.dash_duration = 0
            self.dash_direction = [0, 0]
            self.spike_rotation_angle = 0

    def take_dmg(self, game, dmg):
        self.health -= dmg
        if self.health <= 0:
            if self in game.mini_bosses:
                game.mini_bosses.remove(self)

            game.effects.append(Effect(self.pos, self.size * 7, self.color, 0.12, "ripple"))
            game.score += 1000
            game.player.exp += self.exp_value
            Pickup.drop(self, game.pickups)

    def move(self, game, avoid_radius=0):
        if self.dash_cooldown > 0:
            super().move(game, avoid_radius)
            self.dash_cooldown -= 1
        else:
            self.move_normal_mb(game)

    def move_normal_mb(self, game):
        if self.dash_duration > 0:
            # dash
            dash_speed = self.speed * 20
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
        light_gray = (192, 192, 192)

        radius = self.size
        self.draw_hp_bar(screen, radius)

        if self.enemy_type == 'normal_mb':
            pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), int(radius * 0.25))
            arc_radius = radius * 0.6
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

                x3 = self.pos[0] + radius * math.cos(next_angle)
                y3 = self.pos[1] + radius * math.sin(next_angle)

                pygame.draw.polygon(screen, light_gray, [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])

    def draw_hp_bar(self, screen, radius):
        # draw hp bar
        hp_bar_width = self.size * 1.2
        hp_bar_height = 5
        hp_bar_x = int(self.pos[0] - hp_bar_width / 2)
        hp_bar_y = int(self.pos[1] - radius - hp_bar_height - 15)  # 15 pixels above the miniboss

        # Background of HP bar (dark gray)
        pygame.draw.rect(screen, (120, 120, 120), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))

        # Foreground of HP bar (red)
        health_percentage = self.health / self.max_health
        current_hp_width = int(hp_bar_width * health_percentage)
        pygame.draw.rect(screen, (255, 0, 0), (hp_bar_x, hp_bar_y, current_hp_width, hp_bar_height))
