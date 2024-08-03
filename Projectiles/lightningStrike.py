import pygame
import math
import random

import general
from effect import Effect


class LightningStrike:
    def __init__(self, origin, targets, struck_enemies, player_origin):
        self.origin = origin
        self.targets = targets
        self.struck_enemies = struck_enemies
        self.player_origin = player_origin

        self.sons = []
        self.get_sons()

        self.zap_duration = random.uniform(1, 3)

        self.color = (0, 128, 255)

    def get_sons(self):
        curr_struck = []

        if len(self.targets) == 0:
            return

        # first connection is guaranteed
        while self.player_origin and len(curr_struck) == 0:
            targets = general.get_closest(self.origin.pos, self.targets, self.struck_enemies, 0.2, k=1)
            if len(targets) > 0:
                target = targets[0]
                self.struck_enemies.append(target)
                curr_struck.append(target)

        branches = random.choices([0, 1, 2, 3], weights=[0.35, 0.35, 0.2, 0.1])[0]
        targets = general.get_closest(self.origin.pos, self.targets, self.struck_enemies, 0.2, k=branches)
        if len(targets) > 0:
            self.struck_enemies.extend(targets)
            curr_struck.extend(targets)

        for entity in curr_struck:
            self.sons.append(LightningStrike(entity, self.targets, self.struck_enemies, False))

    def dmg_enemies(self, game):
        if not self.player_origin:
            self.origin.take_dmg(game, game.player.dmg)
            self.origin.add_dot("zap", game.player.dmg / 3, self.zap_duration, 0.33)

        for son in self.sons:
            segment_duration = min(self.zap_duration, son.zap_duration)
            game.effects.append(Effect([self.origin.pos, son.origin.pos], 0, 2, self.color,
                                       segment_duration, "jagged_line"))
            son.dmg_enemies(game)

    def draw(self, screen):
        return

