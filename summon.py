import numpy as np
import pygame
import math
import random
from Projectiles.projectile import Projectile
from entity import Entity
from pickup import Pickup


class Summon(Entity):
    def __init__(self, pos, angle, summon_type):
        spawn_angle = random.uniform(0, 2 * math.pi)
        super().__init__([pos[0] + 30 * math.cos(spawn_angle), pos[1] + 30 * math.sin(spawn_angle)])

        self.summon_type = summon_type
        self.angle = angle

        self.max_lvl = 5
        self.exp_to_level = 10

        self.move_timer = 0
        self.action_timer = 0

        # Set attributes based on type
        if summon_type == "spinning swords":
            self.dmg = 1
            self.speed = 2.3
            self.size = 5

        elif summon_type == "enchanted sword":
            self.dmg = 0.5
            self.speed = 1
            self.size = 8
            self.target = None
            self.direction = [0, 0]

        elif summon_type == "healer":
            self.dmg = 0
            self.speed = 3
            self.size = 5

        elif summon_type == "robo helper":
            self.dmg = 0
            self.speed = 1
            self.size = 5

            self.fire_rate = 10
            self.bullet_dmg = 5
            self.bullet_size = 2

    def move(self, game):
        if self.summon_type == "spinning swords":
            self.move_spinning_swords(game)
        if self.summon_type == "enchanted sword":
            self.move_enchanted_sword(game)
        if self.summon_type == "healer":
            self.move_healer(game)
        if self.summon_type == "robo helper":
            self.move_robo_helper(game)

    def move_spinning_swords(self, game):
        self.angle += (math.pi / 180) * self.speed
        self.angle = self.angle % (2 * math.pi)
        self.pos[0] = game.player.pos[0] + 70 * math.cos(self.angle)
        self.pos[1] = game.player.pos[1] + 70 * math.sin(self.angle)

    def move_enchanted_sword(self, game):
        if self.target and self.target.health > 0:
            self.speed = max(self.speed + 0.1, 2)
            target_pos = np.array(self.target.pos)
            if self.action_timer % 30 == 0:
                self.direction = target_pos - self.pos
                self.angle = math.atan2(self.direction[1], self.direction[0])
            self.pos = self.pos + np.array([math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed])

            if np.sqrt(((self.pos - self.target.pos) ** 2).sum()) < self.target.size:
                self.speed /= 2
        else:
            self.speed = 1
            self.pos = self.pos + np.array([math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed])
            if len(game.enemies) > 0:
                self.target = random.choice(game.enemies + game.mini_bosses)

    def move_healer(self, game):
        dx = game.player.pos[0] - self.pos[0]
        dy = game.player.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist > 50:
            dx, dy = dx / dist, dy / dist  # Normalize

            self.pos[0] += dx * self.speed
            self.pos[1] += dy * self.speed

    def move_robo_helper(self, game):
        self.move_timer += 1

        dx = game.player.pos[0] - self.pos[0]
        dy = game.player.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist > 600:
            dx, dy = dx / dist, dy / dist  # Normalize

            self.pos[0] += dx * self.speed
            self.pos[1] += dy * self.speed
        else:
            if self.move_timer % 180 == 0:
                self.angle = random.uniform(0, 2 * math.pi)
            random_dx = math.cos(self.angle)
            random_dy = math.sin(self.angle)

            self.pos[0] += random_dx * self.speed
            self.pos[1] += random_dy * self.speed

    def action(self, game):
        self.action_timer += 1

        if self.summon_type == "healer":
            if 585 - 40 * self.lvl < self.action_timer < 600 - 40 * self.lvl:
                game.player.health = min(game.player.max_health, game.player.health + self.lvl)

            if self.action_timer == 600 - 40 * self.lvl:
                self.action_timer = 0
                self.add_exp(1)

        if self.summon_type == "robo helper":
            if self.action_timer >= self.fire_rate and len(game.enemies) > 0:
                enemy = random.choice(game.enemies + game.mini_bosses)
                angle = (math.atan2(enemy.pos[1] - self.pos[1], enemy.pos[0] - self.pos[0]))
                game.player_projectiles.append(Projectile(self.pos, angle, 10, "circle", (192, 192, 192),
                                                          self.bullet_size, self.bullet_dmg, self))
                self.action_timer = 0

            if self.move_timer % 600 == 0:
                game.pickups.append(Pickup(self.pos[0], self.pos[1], "ammo"))

    def draw(self, screen):
        if self.summon_type in ["spinning swords", "enchanted sword"]:
            angle = self.angle if self.summon_type == "enchanted sword" else self.angle + math.pi / 2
            handle_end_pos = self.pos[0] + 10 * math.cos(angle), self.pos[1] + 10 * math.sin(angle)
            blade_end_pos = handle_end_pos[0] + 30 * math.cos(angle), handle_end_pos[1] + 30 * math.sin(angle)

            armguard_pos = self.pos[0] + 10 * math.cos(angle), self.pos[1] + 10 * math.sin(angle)
            armguard_start_pos = armguard_pos[0] - 10 * math.cos(angle + math.pi / 2), armguard_pos[1] - 10 * math.sin(angle + math.pi / 2)
            armguard_end_pos = armguard_pos[0] + 10 * math.cos(angle + math.pi / 2), armguard_pos[1] + 10 * math.sin(angle + math.pi / 2)

            if self.summon_type == "spinning swords":
                pygame.draw.line(screen, (192, 192, 192), self.pos, blade_end_pos, 6)
                pygame.draw.line(screen, (139, 69, 19), self.pos, handle_end_pos, 8)
                pygame.draw.line(screen, (255, 255, 0), armguard_start_pos, armguard_end_pos, 6)

            else:
                pygame.draw.line(screen, (0, 200, 200), armguard_pos, blade_end_pos, 12)
                pygame.draw.line(screen, (30, 200, 200), self.pos, handle_end_pos, 4)
                pygame.draw.line(screen, (30, 200, 200), armguard_start_pos, armguard_end_pos, 6)

        if self.summon_type == "healer":
            surface = pygame.Surface((70, 70), pygame.SRCALPHA)

            for i in range(4, -1, -1):
                color = (255, 255, 255) if i == 0 else (255, 0, 114, 255 - 55 * i)

                pygame.draw.rect(surface, color,
                                 pygame.Rect((surface.get_width() // 2 - 5 - 2*i, surface.get_height() // 2 - i, 17 + 4*i, 7 + 2*i)))

                pygame.draw.rect(surface, color,
                                 pygame.Rect(surface.get_width() // 2 - i, surface.get_height() // 2 - 5 - 2*i, 7+2*i, 30 + 4*i))

            screen.blit(surface, (self.pos[0], self.pos[1]))

        if self.summon_type == "robo helper":
            color = (255, 0, 0) if (self.move_timer % 600 < 15 or self.move_timer % 600 > 585) else (0, 255, 0)
            pygame.draw.rect(screen, color,
                             pygame.Rect((int(self.pos[0]) - self.size // 2 - 6, int(self.pos[1]) - self.size // 2 - 6,
                                          self.size + 12, self.size + 12)))

            pygame.draw.rect(screen, (192, 192, 192),
                             pygame.Rect((int(self.pos[0]) - self.size // 2 - 3, int(self.pos[1]) - self.size // 2 - 3,
                                          self.size + 6, self.size + 6)))

    def draw_heal(self, screen, player):
        for i in range(2, -1, -1):
            color = (255, 255, 255) if i == 0 else (255, 0, 114, 255 - 55 * i)
            pygame.draw.line(screen, color, (self.pos[0] + 35, self.pos[1] + 35), player.pos, 1 + 2 * i)
