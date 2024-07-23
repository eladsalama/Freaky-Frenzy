import pygame

from player import Player
from enemy import Enemy
from shootingEnemy import ShootingEnemy
from upgraderEnemy import UpgraderEnemy
from miniBoss import MiniBoss
from projectile import Projectile
from upgrade import Upgrade
import random
import math


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Freaky Frenzy")

        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        self.player = Player(self.WIDTH // 2, self.HEIGHT // 2)
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
                self.player.shoot(self.player_projectiles)
                self.shoot_delay = 0

        self.update_movement()
        self.update_upgrades()

        # Enemies
        if not self.freeze:
            for enemy in self.enemies:
                if enemy.shooting:
                    enemy.shoot(self.player, self.enemy_projectiles)

                if enemy.enemy_type == "upgrader":
                    enemy.upgrade_enemies(self)

            # Spawn enemies
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_delay and len(self.enemies) < self.max_enemies:
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

            if self.player.lvl % 3 == 0:
                self.paused = True
                Upgrade.generate_upgrade(self, self.WIDTH, self.HEIGHT, self.font)
                self.paused = False

            self.enemy_spawn_delay = max(10, int(self.enemy_spawn_delay * 0.97))

            if self.player.lvl % 30 == 0:
                self.max_minibosses += 1

    def update_movement(self):
        self.player.move(pygame.key.get_pressed())

        for proj in self.player_projectiles:
            proj.move(self)

        for summon in self.summons:
            summon.move(self)

        if not self.freeze:
            for enemy in self.enemies:
                enemy.move(self)

            for mb in self.mini_bosses:
                mb.move(self)

            for proj in self.enemy_projectiles:
                proj.move(self)

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

        for proj in self.enemy_projectiles:
            proj.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for miniboss in self.mini_bosses:
            miniboss.draw(self.screen)

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
            enemy_type = random.choices(["normal", "tank", "archer", "upgrader"], weights=[0.70, 0.10, 0.15, 0.05])[0]
            #enemy_type = random.choices(["normal", "tank", "archer"], weights=[0, 0, 1])[0]

            enemy = None

            if enemy_type in ["normal", "tank"]:
                enemy = Enemy([x, y], enemy_type, self.player.lvl)
            elif enemy_type in ["archer"]:
                enemy = ShootingEnemy([x, y], enemy_type, self.player.lvl)
            elif enemy_type in ["upgrader"]:
                enemy = UpgraderEnemy([x, y], enemy_type, self.player.lvl)

            self.enemies.append(enemy)

        if difficulty == 'miniboss':
            miniBoss_type = random.choices(["normal_mb"], weights=[1])[0]
            miniboss = MiniBoss([x, y], miniBoss_type, self.player.lvl)
            self.mini_bosses.append(miniboss)

    def check_collisions(self):
        all_enemies = self.enemies + self.mini_bosses
        for proj in self.player_projectiles:
            if proj.proj_type == "normal":
                for enemy in all_enemies:
                    if math.hypot(proj.x - enemy.pos[0], proj.y - enemy.pos[1]) < enemy.size + proj.size:
                        enemy.take_dmg(self, proj.dmg)

                        if self.player.fork_lvl > 0:
                            self.player_projectiles.remove(proj)

                            if random.random() < 0.3 + 0.05 * self.player.fork_lvl:
                                lvl_increase = 0.5 + 0.1 * self.player.fork_lvl
                                self.player_projectiles.extend([Projectile(proj.x, proj.y, proj.angle + math.pi / 12 * i,
                                                                self.player.bullet_color, self.player.bullet_size * lvl_increase, self.player.dmg * lvl_increase, 0)
                                                                for i in range(-1, 2, 2)])
                            break

                        proj.pierce += 1
                        if proj.pierce == self.player.pierce_lvl:
                            self.player_projectiles.remove(proj)
                            break

        for proj in self.enemy_projectiles:
            distance = math.hypot(proj.x - self.player.pos[0], proj.y - self.player.pos[1])

            if self.player.shield_lvl == 0:
                if distance < self.player.size + proj.size:
                    self.player.health -= proj.dmg
                    self.enemy_projectiles.remove(proj)
                    return True

            else:
                if distance < self.player.size + self.player.shield_radius + proj.size:
                    proj_angle = math.atan2(self.player.pos[1] - proj.y, proj.x - self.player.pos[0])

                    # Check if projectile is within shield's arc (now behind the player)
                    if abs(self.player.shield_angle - proj_angle) <= 2 * self.player.shield_size:
                        self.enemy_projectiles.remove(proj)
                        continue

                # If projectile wasn't blocked by shield, check if it hits the player
                if distance < 10 + proj.size:
                    self.player.health -= proj.dmg
                    self.enemy_projectiles.remove(proj)
                    return True

        for enemy in all_enemies:
            dist = math.hypot(self.player.pos[0] - enemy.pos[0], self.player.pos[1] - enemy.pos[1])
            if dist < enemy.size + self.player.size:
                if not isinstance(enemy, MiniBoss):
                    enemy.take_dmg(self, enemy.health)
                self.player.health -= enemy.damage
                return True

            lvl_increment = 1.25 ** self.player.energy_pulse_lvl
            energy_pulse_radius = 50 * lvl_increment
            if self.player.energy_pulse_lvl > 0 and 4500 < pygame.time.get_ticks() - self.player.energy_pulse_timer < 5500 and dist < enemy.size + energy_pulse_radius:
                enemy.take_dmg(self, self.player.dmg * lvl_increment)

        for pickup in self.pickups:
            if math.hypot(self.player.pos[0] - pickup.x, self.player.pos[1] - pickup.y) < 20:
                pickup.apply_pickup(self, pickup.type)
                self.pickups.remove(pickup)

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
        health_text = font.render(f"Health: {self.player.health}", True, WHITE)
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