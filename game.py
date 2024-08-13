import pygame

from background import Background
from options import Options

from player import Player
from camera import Camera

import numpy as np


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Speed")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.options = Options(self)
        self.WIDTH, self.HEIGHT = self.options.resolutions[self.options.current_resolution_index]

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        self.renderer = Background('src/worldmap.png', self.WIDTH, self.HEIGHT)

        self.player = Player([self.WIDTH // 2, self.HEIGHT // 2])
        self.camera = Camera(self.player.pos[:])

        self.rivals = []
        self.effects = []

        self.game_time = 0

        self.running = True
        self.paused = False

    def run(self):
        while self.running:
            self.handle_events()

            if not self.paused:
                self.update()
                self.draw()
            elif self.options.in_options_menu:
                self.options.draw_options_menu()
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
                if event.button == 1:  # left click
                    if self.paused and self.options.in_options_menu:
                        self.options.handle_options_click(event.pos)

                if event.button == 3:  # right click
                    self.camera.locked = 1 - self.camera.locked

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    return

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.camera.zoom *= 1.1  # Zoom in
                elif event.y < 0:
                    self.camera.zoom *= 0.9  # Zoom out
                self.camera.zoom = max(min(self.camera.zoom, 2), 0.5)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.options.in_options_menu:
                        self.options.in_options_menu = False
                    else:
                        self.paused = not self.paused

    def update(self):
        self.game_time += 1 / 60  # Increment game time

        self.update_movement()

        # Check collisions
        self.check_collisions()

    def update_movement(self):
        self.player.move(self, pygame.key.get_pressed())
        self.camera.move(self, pygame.key.get_pressed())

    def correct_overlaps(self, positions, sizes):
        for i in range(len(self.rivals)):
            for j in range(i + 1, len(self.rivals)):
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

    def check_collisions(self):
        rivals = self.rivals
        player_pos = np.array(self.player.pos)

        rival_positions = np.array([r.pos for r in rivals])
        rival_sizes = np.array([r.size for r in rivals])

        # Player vs rivals
        if rival_positions.size > 0:
            distances = np.linalg.norm(rival_positions - player_pos, axis=1)
            collisions = distances < (rival_sizes + self.player.size)

            for i, collides in enumerate(collisions):
                if collides:
                    return True
        return False

    def game_over(self):
        self.screen.fill((0, 0, 0))
        WHITE = (255, 255, 255)
        game_over_text = self.font.render("Game Over", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)

        self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, self.HEIGHT // 2 - 100))
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

    def draw(self):
        self.screen.fill((10, 10, 10))  # Clear screen
        self.renderer.draw(self.screen, self.camera)
        self.player.draw(self)

        for effect in self.effects:
            effect.draw(self.screen)
            if pygame.time.get_ticks() > effect.time_end:
                self.effects.remove(effect)

        self.draw_hud()

    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        WHITE = (255, 255, 255)

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))

        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 40)

        pause_text = font.render("PAUSED", True, (255, 255, 255))
        resume_text = small_font.render("(Press ESC to resume)", True, (255, 255, 255))
        options_text = font.render("Options", True, (255, 255, 255))
        exit_text = font.render("Exit", True, (255, 255, 255))

        self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, self.HEIGHT // 2 - 250))
        self.screen.blit(resume_text, (self.WIDTH // 2 - resume_text.get_width() // 2, self.HEIGHT // 2 - 210))
        self.screen.blit(options_text, (self.WIDTH // 2 - options_text.get_width() // 2, self.HEIGHT // 2 - 125))
        self.screen.blit(exit_text, (self.WIDTH // 2 - exit_text.get_width() // 2, self.HEIGHT // 2))

        options_rect = options_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 110))
        exit_rect = options_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))

        if options_rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.options.in_options_menu = True

        if exit_rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.running = False
