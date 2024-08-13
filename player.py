import numpy as np
import pygame
import math

from entity import Entity


class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos)

        self.steering_angle = self.angle
        self.speed = 0.0
        self.max_speed = 7.0
        self.acceleration_rate = 0.05
        self.acceleration_rate_reverse = 0.04
        self.brake_rate = 0.2
        self.turn_rate = 0.035
        self.grip = 0.02
        self.friction = 0.02
        self.reverse = False

    def move(self, game, keys):
        # Acceleration
        if keys[pygame.K_w]:
            if self.reverse:
                self.reverse = False
            self.speed = min(self.max_speed, self.speed + self.acceleration_rate)

        # Braking
        elif keys[pygame.K_s]:
            if self.speed > 0:
                self.brake(self.brake_rate)
            else:
                if not self.reverse:
                    self.reverse = True
                self.speed = max(-self.max_speed, self.speed - self.acceleration_rate_reverse)

        # Steering
        turn_cap = (self.angle - math.pi / 10, self.angle + math.pi / 16)
        dynamic_turn_rate = (0.8 + abs(self.speed) / self.max_speed) * self.turn_rate

        steer_direction = 0
        if keys[pygame.K_a]:
            steer_direction = 1 if self.reverse else -1
            self.steering_angle += steer_direction * dynamic_turn_rate
            self.steering_angle = max(turn_cap[0], min(self.steering_angle, turn_cap[1]))

        elif keys[pygame.K_d]:
            steer_direction = -1 if self.reverse else 1
            self.steering_angle += steer_direction * dynamic_turn_rate
            self.steering_angle = max(turn_cap[0], min(self.steering_angle, turn_cap[1]))

        # Drift
        drift = 0
        if keys[pygame.K_e]:
            drift = math.pi / 12 * steer_direction * (abs(self.speed) / self.max_speed)
            self.brake(self.brake_rate / 3)

        # Coasting
        self.speed = math.copysign(max(0.0, abs(self.speed) - self.friction), self.speed)

        # Update position and angle
        if abs(self.speed) > 0:
            self.angle += (self.steering_angle + drift - self.angle)
            self.velocity_angle = (1 - self.grip) * self.velocity_angle + self.grip * self.angle
            self.pos[0] += self.speed * math.sin(self.velocity_angle)
            self.pos[1] -= self.speed * math.cos(self.velocity_angle)

    def brake(self, brake_rate):
        self.speed = math.copysign(max(0, abs(self.speed) - brake_rate), self.speed)

    def draw(self, game):
        width = 36 * game.camera.zoom
        length = 70 * game.camera.zoom

        surface = pygame.Surface((width, length), pygame.SRCALPHA)

        # Draw player components
        pygame.draw.rect(surface, (172, 172, 172),
                         pygame.Rect((surface.get_width() // 2, surface.get_height() // 2 * 0.98, width, length)))
        pygame.draw.rect(surface, self.color,
                         pygame.Rect((surface.get_width() // 2, surface.get_height() // 2, width, length)))
        pygame.draw.rect(surface, (173, 216, 230),
                         pygame.Rect((surface.get_width() // 2 * 1.15, surface.get_height() // 2 * 1.27, width * 0.4,
                                      length // 8)))

        rotated_surf = pygame.transform.rotate(surface, math.degrees(-self.angle))

        # Calculate the position on the screen based on the camera's position
        center = np.array(self.pos) - np.array(game.camera.pos)  # The player's world position relative to the camera
        center = (center * game.camera.zoom) + np.array(
            [game.WIDTH // 2, game.HEIGHT // 2])  # Adjust for camera zoom and screen position

        # Draw the player
        game.screen.blit(rotated_surf, rotated_surf.get_rect(center=center).topleft)
