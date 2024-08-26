import random

from entity import Entity
from pickup import Pickup


class Enemy(Entity):
    def __init__(self, pos, enemy_type, player_lvl):
        super().__init__(pos)

        self.enemy_type = enemy_type

        self.health = 1 + player_lvl // 5
        self.damage = random.randint(5, 10) + player_lvl // 5
        self.speed = 2 + 0.25 * player_lvl // 15
        self.max_speed = self.speed
        self.avoid_radius = 0

        self.color = (180, 180, 180)
        self.color_secondary = (70, 70, 70)
        self.bullet_color = (230, 230, 230)

        self.shooting = False

        self.upgraded = False
        self.upgrader = None

    def take_dmg(self, game, dmg):
        super().take_dmg(game, dmg)

        if self.health <= 0:
            if self in game.enemies:
                game.enemies.remove(self)

            if game.player.omnivamp_lvl > 0 and random.random() < 0.25:
                Pickup.drop(self, game.pickups, 'omnivamp_health')

            # upgrade
            if self.upgraded and self in self.upgrader.upgraded_enemies:
                self.upgrader.upgraded_enemies.remove(self)
            if self.enemy_type[:3] == "upg":
                for enemy in self.upgraded_enemies:
                    enemy.upgrade(self.enemy_type, revert=True)

            # reward
            game.score += 1
            game.player.exp += int(self.exp_value * 1.15 ** (game.player.lvl % 10))
            Pickup.drop(self, game.pickups)

    def upgrade(self, upgrader_type, revert):
        if upgrader_type == "upg_lightning":
            self.upgrade_lightning(revert)
        elif upgrader_type == "upg_fire":
            self.upgrade_fire(revert)
        elif upgrader_type == "upg_frost":
            self.upgrade_frost(revert)

        if not revert:
            self.upgraded = True
            self.exp_value *= 2

        else:
            self.upgraded = False
            self.exp_value //= 2

    def upgrade_lightning(self, revert):
        pass

    def upgrade_frost(self, revert):
        pass

    def upgrade_fire(self, revert):
        pass