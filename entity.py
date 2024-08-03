import random
import pygame


class Entity:
    def __init__(self, pos):
        self.pos = pos
        self.angle = 0
        self.size = 10

        self.lvl = 1
        self.max_lvl = 999
        self.exp = 0
        self.exp_to_level = 30

        self.health = 100
        self.max_health = self.health
        self.speed = 5
        self.max_speed = self.speed

        self.color = (25, 255, 40)
        self.original_color = self.color

        self.dot_effect = None

    def add_exp(self, amount):
        self.exp += amount

        if self.exp >= self.exp_to_level and self.lvl < self.max_lvl:
            self.level_up()

    def level_up(self):
        self.lvl += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.05)

    def take_dmg(self, game, dmg):
        self.health -= dmg

    def add_dot(self, dot_type, dmg, duration, interval):
        duration = int(duration * 60)
        interval = int(interval * 60)
        self.dot_effect = {'type': dot_type, 'dmg': dmg, 'duration': duration, 'interval': interval, 'timer': 0,
                           'cooldown': 120}

    def apply_dot(self, game):
        self.take_dmg(game, self.dot_effect['dmg'])

        if self.dot_effect['type'] == "zap":
            self.color = (random.randint(150, 200), random.randint(150, 200), 255)
            self.speed *= 0.7
        if self.dot_effect['type'] == "freeze":
            self.color = (173, 216, 230)
            self.speed *= 0.3
        if self.dot_effect['type'] == "burn":
            self.color = (222, 69, 0)
            self.speed *= 1.2

    def update(self, game):
        if self.dot_effect:
            self.dot_effect['timer'] += 1

            if self.dot_effect['timer'] < self.dot_effect['duration']:

                if self.dot_effect['timer'] % self.dot_effect['interval'] == 0:
                    self.apply_dot(game)

            else:
                self.dot_effect['cooldown'] -= 1
                if self.dot_effect['type'] == "zap":
                    self.color = (255, 255, 255)

                if self.dot_effect['cooldown'] <= 0:
                    self.dot_effect = None
                    self.speed = self.max_speed
                    self.color = self.original_color

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