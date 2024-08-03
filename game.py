import pygame

from Enemies.mb_dasher import MB_Dasher
from Enemies.mb_shooter import MB_Shooter

from Enemies.warrior import Warrior
from Enemies.archer import Archer
from Enemies.tank import Tank
from Enemies.evolver import Evolver
from effect import Effect

from player import Player
from Enemies.miniBoss import MiniBoss
from Projectiles.projectile import Projectile
from summon import Summon
from upgrade import Upgrade

import random
import math
import numpy as np


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Freaky Frenzy")

        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        self.player = Player([self.WIDTH // 2, self.HEIGHT // 2])
        self.summons = []
        self.enemies = []
        self.mini_bosses = []
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.pickups = []
        self.effects = []
        self.max_enemies = 10
        self.max_minibosses = 0
        self.enemy_spawn_delay = 120
        self.enemy_spawn_timer = 0

        self.running = True
        self.paused = False
        self.freeze = False
        self.freeze_time = 0

        self.score = 0
        self.game_time = 0

        self.shooting = False
        self.shoot_delay = 0

    def run(self):
        while self.running:
            self.handle_events()

            if not self.paused:
                self.update()
                self.draw()
            else:
                self.draw_pause_menu()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.shooting = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.shooting = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

    def update(self):
        self.game_time += 1 / 60  # Increment game time

        # Increase difficulty over time
        self.max_enemies = 10 + int(self.game_time / 10)  # Add one more max enemy every 10 seconds

        # Player
        self.player.aim()
        if self.shooting:
            self.shoot_delay += 1
            if self.shoot_delay >= self.player.fire_rate:
                self.player.shoot(self)
                self.shoot_delay = 0

        self.update_movement()
        self.update_projectiles()
        self.update_upgrades()

        # Enemies
        all_enemies = self.enemies + self.mini_bosses
        if not self.freeze:
            for enemy in all_enemies:
                enemy.update(self)

                if enemy.shooting:
                    enemy.shoot(self)

                if isinstance(enemy, Evolver):
                    enemy.upgrade_enemies(self)

            # Spawn enemies
            self.enemy_spawn_timer += 1
            if (len(self.mini_bosses) == 0 and self.enemy_spawn_timer >= self.enemy_spawn_delay
                    and len(self.enemies) < self.max_enemies):
                self.spawn_enemy()
                self.enemy_spawn_timer = 0

            if self.player.lvl % 30 == 0 and len(self.mini_bosses) < self.max_minibosses:
                self.spawn_enemy(difficulty='miniboss')

        else:
            timer_duration = 3000  # 3 seconds in milliseconds
            if pygame.time.get_ticks() - self.freeze_time > timer_duration:
                self.freeze = False
                self.player.fire_rate *= 5

        # Check collisions
        if self.check_collisions():
            if self.player.health <= 0:
                self.game_over()
                self.__init__()  # Reset game state

        # level-up
        if self.player.exp >= self.player.exp_to_level:
            self.player.level_up()
            self.effects.append(Effect(self.player.pos, 0, 10, (173, 216, 230), 1, "arrow_up"))

            if self.player.lvl % 3 == 0:
                self.paused = True
                Upgrade.generate_upgrade(self, self.WIDTH, self.HEIGHT, self.font)
                self.paused = False

            self.enemy_spawn_delay = max(10, int(self.enemy_spawn_delay * 0.95))

            if self.player.lvl % 30 == 0:
                self.max_minibosses += 1

    def update_movement(self):
        self.player.move(pygame.key.get_pressed())

        for mb in self.mini_bosses:
            mb.move(self)

        for summon in self.summons:
            summon.action(self)
            summon.move(self)

        if not self.freeze:
            self.update_movement_enemies()

    def update_movement_enemies(self):
        all_enemies = self.enemies + self.mini_bosses
        if not all_enemies:
            return

        positions = np.array([enemy.pos for enemy in all_enemies])
        sizes = np.array([enemy.size for enemy in all_enemies])
        speeds = np.array([enemy.speed for enemy in all_enemies])
        avoid_radii = np.array([enemy.avoid_radius for enemy in all_enemies])

        # Calculate directions to player
        player_pos = np.array(self.player.pos)
        directions = player_pos - positions
        distances = np.linalg.norm(directions, axis=1)
        directions = directions.astype(float)
        distances = distances.astype(float)
        directions /= distances[:, np.newaxis]  # Normalize

        # Determine movement direction based on individual avoid_radius
        direction_multiplier = np.where(distances >= avoid_radii, 1,
                                        np.where(distances <= avoid_radii * 0.9, -1, 0))

        # Calculate new positions
        new_positions = positions + direction_multiplier[:, np.newaxis] * directions * speeds[:, np.newaxis]

        # Correct overlaps
        self.correct_overlaps(new_positions, sizes)

        # Update enemy positions
        for enemy, new_pos in zip(all_enemies, new_positions):
            enemy.pos[0] = new_pos[0]
            enemy.pos[1] = new_pos[1]

    def correct_overlaps(self, positions, sizes):
        for i in range(len(self.enemies)):
            for j in range(i + 1, len(self.enemies)):
                distance = np.linalg.norm(positions[i] - positions[j])
                min_distance = sizes[i] + sizes[j]

                if distance < min_distance:
                    # Calculate the overlap
                    overlap = min_distance - distance

                    # Calculate the direction of separation
                    direction = positions[i] - positions[j]
                    direction /= distance

                    # Move enemies apart
                    positions[i] += direction * overlap / 2
                    positions[j] -= direction * overlap / 2

    def update_projectiles(self):
        self.update_projectile_group(self.player_projectiles)
        if not self.freeze:
            self.update_projectile_group(self.enemy_projectiles)

    def update_projectile_group(self, projectiles):
        if not projectiles:
            return

        positions = np.array([p.pos for p in projectiles])
        velocities = np.array([p.velocity for p in projectiles])

        new_positions = positions + velocities

        # Update homing projectiles
        for i, proj in enumerate(projectiles):
            if proj.proj_type == "homing":
                proj.update_homing_projectile(self, new_positions[i])
            else:
                proj.pos = new_positions[i]

        # Remove out-of-bounds projectiles
        valid_indices = ((new_positions[:, 0] >= -50) &
                         (new_positions[:, 0] <= self.WIDTH + 50) &
                         (new_positions[:, 1] >= -50) &
                         (new_positions[:, 1] <= self.HEIGHT + 50))

        projectiles[:] = [proj for i, proj in enumerate(projectiles) if valid_indices[i]]

    def update_upgrades(self):
        # Magnet, OmniVamp
        for pickup in self.pickups:
            pickup.move(self.player)

        # Energy Pulse
        if self.player.energy_pulse_lvl > 0:
            if pygame.time.get_ticks() - self.player.energy_pulse_timer > 5500:
                self.player.energy_pulse_timer = pygame.time.get_ticks()

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.player.draw(self.screen)

        for proj in self.player_projectiles:
            proj.draw(self.screen)

        for summon in self.summons:
            summon.draw(self.screen)

            if summon.summon_type == "healer":
                if 570 - 40 * summon.lvl < summon.action_timer < 600 - 40 * summon.lvl:
                    summon.draw_heal(self.screen, self.player)

        for proj in self.enemy_projectiles:
            proj.draw(self.screen)

        for enemy in self.enemies + self.mini_bosses:
            enemy.draw(self.screen)

        if len(self.mini_bosses) > 0:
            self.mini_bosses[0].draw_screen_glow(self.screen)

        for pickup in self.pickups:
            pickup.draw(self.screen)
            if pygame.time.get_ticks() - pickup.spawn_time > 10000:
                self.pickups.remove(pickup)

        for effect in self.effects:
            effect.draw(self.screen)
            if pygame.time.get_ticks() > effect.time_end:
                self.effects.remove(effect)

        self.draw_hud()

    def spawn_enemy(self, difficulty='normal'):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, self.WIDTH)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, self.WIDTH)
            y = self.HEIGHT
        elif side == 'left':
            x = 0
            y = random.randint(0, self.HEIGHT)
        else:  # right
            x = self.WIDTH
            y = random.randint(0, self.HEIGHT)

        if difficulty == 'normal':
            enemy_type = random.choices(["warrior", "tank", "archer", "evolver"], weights=[0.73, 0.10, 0.15, 0.02])[0]
            #enemy_type = random.choices(["normal", "tank", "archer", "evolver"], weights=[0, 1, 0, 0])[0]

            enemy = None

            if enemy_type == "warrior":
                enemy = Warrior([x, y], enemy_type, self.player.lvl)
            elif enemy_type == "tank":
                enemy = Tank([x, y], enemy_type, self.player.lvl)
            elif enemy_type == "archer":
                enemy = Archer([x, y], enemy_type, self.player.lvl)
            elif enemy_type == "evolver":
                upgrader_type = random.choices(["upg_lightning", "upg_frost", "upg_fire"])[0]
                enemy = Evolver([x, y], upgrader_type, self.player.lvl)

            self.enemies.append(enemy)

        if difficulty == 'miniboss':
            miniBoss_type = random.choice(["mb_dasher", "mb_shooter"])

            miniboss = None
            if miniBoss_type == "mb_dasher":
                miniboss = MB_Dasher([x, y], miniBoss_type, self.player.lvl)
            elif miniBoss_type == "mb_shooter":
                miniboss = MB_Shooter([x, y], miniBoss_type, self.player.lvl)
            self.mini_bosses.append(miniboss)

    def check_collisions(self):
        all_enemies = self.enemies + self.mini_bosses
        player_pos = np.array(self.player.pos)

        # Convert positions and sizes of enemies and projectiles to NumPy arrays
        enemy_positions = np.array([enemy.pos for enemy in all_enemies])
        enemy_sizes = np.array([enemy.size for enemy in all_enemies])
        enemy_damages = np.array([enemy.damage for enemy in all_enemies])

        player_proj_positions = np.array([proj.pos for proj in self.player_projectiles])
        player_proj_sizes = np.array([proj.size for proj in self.player_projectiles])

        enemy_proj_positions = np.array([proj.pos for proj in self.enemy_projectiles])
        enemy_proj_sizes = np.array([proj.size for proj in self.enemy_projectiles])

        to_remove_player_proj = set()
        to_remove_enemy_proj = set()
        to_remove_enemies = set()
        to_remove_pickups = set()

        # Player projectiles vs enemies
        if enemy_positions.size > 0 and player_proj_positions.size > 0:
            distances = np.sqrt(((player_proj_positions[:, None, :] - enemy_positions[None, :, :]) ** 2).sum(axis=2))
            collisions = distances < (player_proj_sizes[:, None] + enemy_sizes[None, :])

            for proj_idx, enemy_idx in np.argwhere(collisions):
                if proj_idx in to_remove_player_proj or enemy_idx in to_remove_enemies:
                    continue

                enemy = all_enemies[enemy_idx]
                proj = self.player_projectiles[proj_idx]
                enemy.take_dmg(self, proj.dmg)
                self.effects.append(Effect(enemy.pos, proj.angle, 3, enemy.color, 0.5, "dot_splatter"))

                if self.player.bullet_dot in ["freeze", "burn"] and not isinstance(enemy, MiniBoss):
                    dot = 0 if self.player.bullet_dot == "freeze" else self.player.dmg / 1.5
                    enemy.add_dot(self.player.bullet_dot, dot, 1, 0.33)

                if enemy.health <= 0 and isinstance(proj.shooter, Summon):
                    proj.shooter.add_exp(1)

                if self.player.fork_lvl > 0:
                    to_remove_player_proj.add(proj_idx)

                    if random.random() < 0.3 + 0.05 * self.player.fork_lvl:
                        lvl_increase = 0.5 + 0.1 * self.player.fork_lvl
                        new_projectiles = [Projectile(proj.pos, proj.angle + math.pi / 12 * i, 10,
                                           self.player.bullet_shape, self.player.bullet_color,
                                           self.player.bullet_size * lvl_increase,
                                           self.player.dmg * lvl_increase, 0)
                                           for i in range(-1, 2, 2)]
                        self.player_projectiles.extend(new_projectiles)
                    continue

                proj.pierce += 1
                if proj.pierce == self.player.pierce_lvl:
                    to_remove_player_proj.add(proj_idx)
                    continue

        # Enemy projectiles vs player
        if enemy_proj_positions.size > 0:
            distances = np.linalg.norm(enemy_proj_positions - player_pos, axis=1)
            collisions = distances < (enemy_proj_sizes + self.player.size)

            for i, collides in enumerate(collisions):
                if collides:
                    proj = self.enemy_projectiles[i]
                    if self.player.shield_lvl == 0:
                        self.player.take_dmg(self, proj.dmg)
                        to_remove_enemy_proj.add(i)
                    else:
                        proj_angle = math.atan2(self.player.pos[1] - proj.pos[1], proj.pos[0] - self.player.pos[0])
                        if distances[i] < self.player.size + self.player.shield_radius + proj.size:
                            if abs(self.player.shield_angle - proj_angle) <= 2 * self.player.shield_size:
                                to_remove_enemy_proj.add(i)
                                continue
                            elif distances[i] < 10 + proj.size:
                                self.player.take_dmg(self, proj.dmg)
                                to_remove_enemy_proj.add(i)
                                continue

        # Player vs enemies
        if enemy_positions.size > 0:
            distances = np.linalg.norm(enemy_positions - player_pos, axis=1)
            collisions = distances < (enemy_sizes + self.player.size)

            for i, collides in enumerate(collisions):
                if collides:
                    if i in to_remove_enemies:
                        continue
                    enemy = all_enemies[i]
                    if not isinstance(enemy, MiniBoss):
                        enemy.take_dmg(self, enemy.health)
                    self.player.health -= enemy_damages[i]
                    to_remove_enemies.add(i)
                    return True

        # Energy Shield
        lvl_increment = 1.25 ** self.player.energy_pulse_lvl
        energy_pulse_radius = 50 * lvl_increment

        if self.player.energy_pulse_lvl > 0 and 4500 < pygame.time.get_ticks() - self.player.energy_pulse_timer < 5500:
            if enemy_positions.size > 0:
                distances = np.linalg.norm(enemy_positions - player_pos, axis=1)
                collisions = distances < (enemy_sizes + energy_pulse_radius)

                for i, collides in enumerate(collisions):
                    if collides:
                        all_enemies[i].take_dmg(self, self.player.dmg * lvl_increment)

        # Summons vs enemies
        summon_positions = np.array([summon.pos for summon in self.summons])
        summon_sizes = np.array([summon.size for summon in self.summons])

        if summon_positions.size > 0 and enemy_positions.size > 0:
            distances = np.sqrt(((summon_positions[:, None, :] - enemy_positions[None, :, :]) ** 2).sum(axis=2))
            collisions = distances < (summon_sizes[:, None] + enemy_sizes[None, :])

            for summon_idx, enemy_idx in np.argwhere(collisions):
                if enemy_idx in to_remove_enemies:
                    continue
                all_enemies[enemy_idx].take_dmg(self, self.summons[summon_idx].dmg)

        # Player vs pickups
        if len(self.pickups) > 0:
            pickup_positions = np.array([(pickup.x, pickup.y) for pickup in self.pickups])
            pickup_sizes = np.array([20] * len(self.pickups))  # Assuming a fixed size for pickups

            distances = np.linalg.norm(pickup_positions - player_pos, axis=1)
            collisions = distances < pickup_sizes

            for i, collides in enumerate(collisions):
                if collides:
                    if i in to_remove_pickups:
                        continue
                    pickup = self.pickups[i]
                    pickup.apply_pickup(self, pickup.type)
                    to_remove_pickups.add(i)

        # Remove projectiles, enemies, and pickups after processing
        self.player_projectiles = [proj for idx, proj in enumerate(self.player_projectiles) if
                                   idx not in to_remove_player_proj]
        self.enemy_projectiles = [proj for idx, proj in enumerate(self.enemy_projectiles) if
                                  idx not in to_remove_enemy_proj]
        self.enemies = [enemy for idx, enemy in enumerate(self.enemies) if idx not in to_remove_enemies]
        self.mini_bosses = [enemy for idx, enemy in enumerate(self.mini_bosses) if idx not in to_remove_enemies]
        self.pickups = [pickup for idx, pickup in enumerate(self.pickups) if idx not in to_remove_pickups]

        return False

    def game_over(self):
        self.screen.fill((0, 0, 0))
        WHITE = (255, 255, 255)
        game_over_text = self.font.render("Game Over", True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Final Level: {self.player.lvl}", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)

        self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, self.HEIGHT // 2 - 100))
        self.screen.blit(score_text, (self.WIDTH // 2 - score_text.get_width() // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(level_text, (self.WIDTH // 2 - level_text.get_width() // 2, self.HEIGHT // 2))
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, self.HEIGHT // 2 + 50))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True
        return False

    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        WHITE = (255, 255, 255)
        health_text = font.render(f"Health: {int(self.player.health)}", True, WHITE)
        ammo_text = font.render(f"Ammo: {self.player.ammo}", True, WHITE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.player.lvl}", True, WHITE)
        exp_text = font.render(f"EXP: {self.player.exp}/{self.player.exp_to_level}", True, WHITE)
        time_text = font.render(f"Time: {int(self.game_time)}s", True, WHITE)
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(exp_text, (10, 40))
        self.screen.blit(score_text, (self.WIDTH - 150, 10))
        self.screen.blit(time_text, (self.WIDTH - 150, 40))
        self.screen.blit(health_text, (self.WIDTH - 150, self.HEIGHT - 70))
        self.screen.blit(ammo_text, (self.WIDTH - 150, self.HEIGHT - 40))

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 48)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        resume_text = font.render("Press ESC to resume", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(resume_text, (self.WIDTH // 2 - resume_text.get_width() // 2, self.HEIGHT // 2 + 50))