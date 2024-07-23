import pygame
import math
import random

from projectile import Projectile


class Player:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.size = 10
        self.angle = 0

        self.lvl = 1
        self.exp = 0
        self.exp_to_level = 30

        self.max_health = 100
        self.health = 100

        self.dmg = 1
        self.speed = 5

        self.proj_type = "normal"
        self.ammo = 50  # 50
        self.fire_rate = 3  # 50
        self.bullet_amount = 1
        self.bullet_size = 5
        self.pierce_lvl = 1
        self.fork_lvl = 0
        self.spreadShot = False
        self.bullet_color = (0, 0, 255)

        self.shield_lvl = 0
        self.shield_size = 0
        self.shield_radius = 30
        self.shield_angle = 0
        self.shield_width = 5
        self.shield_color = (0, 255, 255)  # Cyan color
        self.shield_cannons = [None, None, None]
        self.cannon_angle = 0

        self.magnet_lvl = 0
        self.energy_pulse_lvl = 0
        self.energy_pulse_timer = 0

        self.omnivamp_lvl = 0

        self.disabled_upgrades = ["None"]

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.pos[0] += dx
        self.pos[1] += dy

        # Keep player within screen bounds
        self.pos[0] = max(10, min(790, self.pos[0]))
        self.pos[1] = max(10, min(590, self.pos[1]))

    def aim(self):
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pos[0]
        dy = mouse_pos[1] - self.pos[1]
        self.angle = math.atan2(dy, dx)

    def shoot(self, projectiles):
        if self.proj_type == "normal":
            self.shoot_normal(projectiles)

    def shoot_normal(self, projectiles):
        if self.ammo > 0:
            for i in range(0, self.bullet_amount):
                offset_x = math.cos(self.angle) * 20 * i
                offset_y = math.sin(self.angle) * 20 * i
                angle_variance = 0

                if self.spreadShot:
                    if 1 < self.bullet_amount < 5:
                        angle_variance = random.uniform(-math.pi / 12, math.pi / 12)
                    elif self.bullet_amount >= 5:
                        angle_variance = random.uniform(-math.pi / 6, math.pi / 6)

                projectiles.append(Projectile(self.pos[0] + offset_x, self.pos[1] + offset_y, self.angle + angle_variance,
                                              self.bullet_color, self.bullet_size, self.dmg, 0))
            self.ammo -= 1

        if self.shield_lvl == 3:
            projectiles.extend([Projectile(self.shield_cannons[i][0], self.shield_cannons[i][1],
                                           self.cannon_angle + (i - 1) * (math.pi / 6),
                                           self.bullet_color, self.bullet_size, self.dmg, 0) for i in range(3)])

    def level_up(self):
        self.lvl += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.1)  # Increase exp needed for next level

    def draw(self, screen):
        # player
        pygame.draw.circle(screen, (255, 0, 0), (int(self.pos[0]), int(self.pos[1])), self.size)

        # aim line
        end_pos = (int(self.pos[0] + math.cos(self.angle) * 18),
                   int(self.pos[1] + math.sin(self.angle) * 18))
        pygame.draw.line(screen, (255, 0, 0), self.pos, end_pos, 6)

        # shield
        if self.shield_lvl > 0:
            self.shield_angle = math.atan2(end_pos[1] - self.pos[1], self.pos[0] - end_pos[0])
            self.cannon_angle = math.atan2(self.pos[1] - end_pos[1], self.pos[0] - end_pos[0])

            pygame.draw.arc(screen, self.shield_color,
                            (self.pos[0] - self.shield_radius, self.pos[1] - self.shield_radius,
                             self.shield_radius * 2, self.shield_radius * 2),
                            self.shield_angle - self.shield_size, self.shield_angle + self.shield_size,
                            self.shield_width)

        if self.shield_lvl == 3:
            cannon_size = 6  # Define the size of the cannons
            for i in range(3):
                cannon_angle = self.cannon_angle + (i - 1) * (math.pi / 6)

                gap = 3
                cannon_start_pos = (self.pos[0] + (self.shield_radius + gap + cannon_size) * math.cos(cannon_angle),
                                    self.pos[1] + (self.shield_radius + gap + cannon_size) * math.sin(cannon_angle))

                cannon_end_pos = (cannon_start_pos[0] + math.cos(cannon_angle) * cannon_size,
                                  cannon_start_pos[1] + math.sin(cannon_angle) * cannon_size)

                self.shield_cannons[i] = cannon_start_pos
                pygame.draw.line(screen, self.shield_color, cannon_start_pos, cannon_end_pos, self.shield_width)

        # energy pulse
        if self.energy_pulse_lvl > 0 and pygame.time.get_ticks() - self.energy_pulse_timer > 4500:
            radius = 30 * 1.4 ** self.energy_pulse_lvl
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (0, 255, 255, 80), (radius, radius), radius)
            pygame.draw.arc(circle_surface, (0, 255, 255),
                            (0, 0, radius * 2, radius * 2),
                            0, 2 * math.pi, width=3)

            screen.blit(circle_surface, (self.pos[0] - radius, self.pos[1] - radius))
