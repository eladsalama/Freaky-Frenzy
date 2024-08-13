import numpy as np
import pygame
import pygame.math as pgmath

class Camera:
    def __init__(self, initial_pos):
        self.pos = np.array(initial_pos, dtype=float)
        self.pos = pgmath.Vector2(initial_pos[0], initial_pos[1])
        self.last_player_speed = 0
        
        self.locked = False
        self.zoom = 1

    def move(self, game, keys):
        if self.locked:
            self.move_locked(game, keys)
        else:
            self.move_unlocked(game)
            if keys[pygame.K_SPACE]:
                player = game.player
                angle = player.angle
                self.pos = (player.pos[:] + np.array([game.WIDTH / game.HEIGHT * np.sin(angle), -np.cos(angle)]) *
                            game.WIDTH // 6 * player.speed / player.max_speed)
            
    def move_locked(self, game, keys):
        player_pos = np.array(game.player.pos, dtype=float)

        player_speed = game.player.speed
        player_speed_max = game.player.max_speed

        is_accelerating = (keys[pygame.K_w] and player_speed >= self.last_player_speed) or \
                          (keys[pygame.K_s] and player_speed <= self.last_player_speed)
        self.last_player_speed = player_speed

        # Calculate the desired camera position behind the player
        angle = game.player.velocity_angle

        offset = 0 if player_speed == 0 \
            else -np.array([game.WIDTH / game.HEIGHT * np.sin(angle), -np.cos(angle)]) * game.WIDTH // 6
        target = player_pos - offset
        direction = target - self.pos

        player_speed = abs(player_speed)
        dist_to_target = np.linalg.norm(direction)

        speed = player_speed
        if dist_to_target > 0:
            direction /= dist_to_target  # normalize
            if player_speed == 0:
                speed = dist_to_target / 30
            else:
                speed_factor = (0.15 if player_speed / player_speed_max < 0.1 else
                                0.7 if player_speed / player_speed_max < 0.8 else 1.1)
                speed = player_speed * (speed_factor if is_accelerating else 1.1)

        if dist_to_target < 20:
            speed = min(speed, player_speed)

        self.pos += direction * speed

    def move_unlocked(self, game):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        edge_threshold = 50
        camera_speed = 10

        if mouse_x < edge_threshold:
            self.pos[0] -= camera_speed
        elif mouse_x > game.WIDTH - edge_threshold:
            self.pos[0] += camera_speed

        if mouse_y < edge_threshold:
            self.pos[1] -= camera_speed
        elif mouse_y > game.HEIGHT - edge_threshold:
            self.pos[1] += camera_speed
