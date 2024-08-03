import random

import pygame
import math
from Enemies.miniBoss import MiniBoss
from Projectiles.projectile import Projectile
from effect import Effect
from pickup import Pickup


class MB_Shooter(MiniBoss):
    def __init__(self, pos, miniboss_type, player_lvl):
        super().__init__(pos, 'upgrader_archer_mb', player_lvl)
        self.size = 70
        self.max_health = 1000 * 4 ** (player_lvl % 5)
        self.health = self.max_health
        self.damage = 1
        self.speed = 0.7
        self.exp_value = 15
        self.color = (18, 34, 86)
        eye_colors = [(74, 249, 82), (196, 67, 255), (251, 235, 61), (65, 137, 248)]
        self.eye_color = random.choice(eye_colors)
        self.bullet_color = (208, 0, 208)
        self.original_color = self.color

        self.shooting = True
        self.shoot_cooldown = 0

        self.bullet_patterns = [
            self.spiral_pattern,
            self.grid_pattern,
            self.concentric_circles_pattern,
            self.wave_pattern,
            self.targeted_burst_pattern,
            self.starburst_pattern,
            self.spiral_inward_pattern,
            self.expanding_spiral_pattern,
            self.homing_pattern
        ]
        self.current_pattern = 0
        self.pattern_duration = 180  # 3 seconds at 60 FPS
        self.pattern_timer = 0

    def shoot(self, game):
        self.angle = math.atan2(game.player.pos[1] - self.pos[1], game.player.pos[0] - self.pos[0])
        if self.shoot_cooldown <= 0:
            # Perform shoot
            self.bullet_patterns[self.current_pattern](game)

            # Reset cooldown
            self.shoot_cooldown = 15

            # Update pattern
            self.pattern_timer += 1
            if self.pattern_timer >= self.pattern_duration:
                self.current_pattern = (self.current_pattern + 1) % len(self.bullet_patterns)
                self.pattern_timer = 0
        else:
            self.shoot_cooldown -= 1

        # Update pattern timer regardless of whether we shot or not
        self.pattern_timer += 1
        if self.pattern_timer >= self.pattern_duration:
            self.current_pattern = (self.current_pattern + 1) % len(self.bullet_patterns)
            self.pattern_timer = 0

    def spiral_pattern(self, game):
        num_bullets = 10
        for i in range(num_bullets):
            angle = 2 * math.pi * i / num_bullets + game.game_time / 10
            self.create_bullet(game, self.pos, angle, speed=2)

    def grid_pattern(self, game):
        grid_size = 150
        for i in range(0, 800, grid_size):
            self.create_bullet(game, (i, 0), 2 * math.pi / 4, 3)

        for j in range(0, 600, grid_size):
            self.create_bullet(game, (0, j), 2 * math.pi, 3)

    def concentric_circles_pattern(self, game):
        num_circles = 3
        bullets_per_circle = 12
        for j in range(num_circles):
            for i in range(bullets_per_circle):
                angle = 2 * math.pi * i / bullets_per_circle
                self.create_bullet(game, self.pos, angle, speed=4 + j)

    def wave_pattern(self, game):
        waves = 3
        bullets_per_wave = 10
        for j in range(waves):
            for i in range(bullets_per_wave):
                angle = 2 * math.pi * i / bullets_per_wave + (j * math.pi / 4)
                self.create_bullet(game, self.pos, angle, speed=4 + j)

    def targeted_burst_pattern(self, game):
        num_bullets = 5

        for i in range(num_bullets):
            spread = (i - num_bullets // 2) * 0.1
            self.create_bullet(game, self.pos, self.angle + spread, speed=4)

    def starburst_pattern(self, game):
        num_bursts = 5
        bullets_per_burst = 8

        for j in range(num_bursts):
            for i in range(bullets_per_burst):
                angle = 2 * math.pi * i / bullets_per_burst + (j * math.pi / 10)
                self.create_bullet(game, self.pos, angle, speed=4 + j * 0.5)

    def spiral_inward_pattern(self, game):
        num_bullets = 12
        for i in range(num_bullets):
            angle = 2 * math.pi * i / num_bullets + game.game_time / 10
            speed = 6 - (i % 4)  # Decrease speed for inward spiral effect
            self.create_bullet(game, self.pos, angle, speed)

    def expanding_spiral_pattern(self, game):
        num_bullets = 8
        for i in range(num_bullets):
            angle = 2 * math.pi * i / num_bullets + game.game_time / 20
            distance = i * 5  # Increasing distance from the miniboss
            x = self.pos[0] + distance * math.cos(angle)
            y = self.pos[1] + distance * math.sin(angle)
            self.create_bullet(game, (x, y), angle, speed=5)

    def homing_pattern(self, game):
        num_bullets = 1
        for i in range(num_bullets):
            self.create_bullet(game, self.pos, self.angle, speed=3, proj_type="homing", target=game.player)

    def create_bullet(self, game, pos, angle, speed, proj_type="normal", target=None):
        bullet = Projectile((pos[0], pos[1]), angle, speed, 'circle', self.bullet_color, 5, self.damage,
                            self, proj_type, target)
        game.enemy_projectiles.append(bullet)


    def draw(self, screen):
        super().draw_hp_bar(screen)

        # Draw the UFO body
        ufo_rect = pygame.Rect(self.pos[0] - self.size, self.pos[1] - self.size // 2, self.size * 2, self.size)
        pygame.draw.ellipse(screen, self.color, ufo_rect)

        # Draw the UFO dome
        dome_rect = pygame.Rect(self.pos[0] - self.size // 2, self.pos[1] - 0.75 * self.size, self.size, self.size)
        pygame.draw.circle(screen, (3, 14, 32), (self.pos[0], self.pos[1] - 0.31 * self.size), self.size // 2)

        pygame.draw.circle(screen, self.eye_color, (self.pos[0] + 5 * math.cos(self.angle),
                                                 self.pos[1] - 0.27 * self.size + 5 * math.sin(self.angle)), self.size // 4)
        eye_rect = pygame.Rect(self.pos[0] - self.size // 11 + 15 * math.cos(self.angle), self.pos[1] - self.size // 3 + 10 * math.sin(self.angle)
                               , self.size // 8, self.size // 4)
        pygame.draw.ellipse(screen, (15,15,15), eye_rect)
        pygame.draw.arc(screen, (200, 200, 200), dome_rect, 0, 2 * math.pi, 2)

        # Draw lights
        lights = [
            ((self.pos[0] - self.size * 0.65, self.pos[1] - self.size * 0.27), 20),
            ((self.pos[0] - self.size * 0.88, self.pos[1] - self.size * 0.05), 16),
            ((self.pos[0] - self.size * 0.6, self.pos[1] + self.size * 0.27), 14),
            ((self.pos[0], self.pos[1] + self.size * 0.4), 11),
            ((self.pos[0] + self.size * 0.6, self.pos[1] + self.size * 0.27), 14),
            ((self.pos[0] + self.size * 0.88, self.pos[1] - self.size * 0.05), 16),
            ((self.pos[0] + self.size * 0.65, self.pos[1] - self.size * 0.27), 20)
        ]
        for light in lights:
            color = (255,234,0) if (55 < self.pattern_timer < 65 or 145 < self.pattern_timer < 155) else (12, 220, 233)
            pygame.draw.circle(screen, color, light[0], self.size // int(light[1]))
