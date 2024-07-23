import pygame
import math
import random
from summon import Summon


class Upgrade:
    upgrade_options = [{"name": "Wizard", "weight": 0.3, "rarity": "legendary"},
                       {"name": "Death", "weight": 0.3, "rarity": "legendary"},
                       {"name": "Magnet Drops", "weight": 2, "rarity": "epic"},
                       {"name": "Energy Pulse", "weight": 2, "rarity": "epic"},
                       {"name": "Omnivamp", "weight": 2, "rarity": "epic"},
                       {"name": "Spread Shot", "weight": 2, "rarity": "epic"},
                       {"name": "Spinning Swords", "weight": 0, "rarity": "epic"},
                       {"name": "Healer", "weight": 0, "rarity": "epic"},
                       {"name": "Tougher Bullets", "weight": 7, "rarity": "rare"},
                       {"name": "More Bullets", "weight": 7, "rarity": "rare"},
                       {"name": "Better Pierce", "weight": 7, "rarity": "rare"},
                       {"name": "Fork Bullet", "weight": 7, "rarity": "rare"},
                       {"name": "Shield", "weight": 10, "rarity": "uncommon"},
                       {"name": "Faster Shooting", "weight": 10, "rarity": "uncommon"},
                       {"name": "Increased Max Health", "weight": 20, "rarity": "common"},
                       {"name": "Faster Movement", "weight": 23.4, "rarity": "common"},
                       {"name": "None", "weight": 0, "rarity": "common"}]

    #upgrade_options = [{"name": "Spinning Swords", "weight": 50, "rarity": "epic"},
    #                   {"name": "Healer", "weight": 50, "rarity": "epic"},]

    rarity_colors = {"common": (255, 255, 255),  # White
                     "uncommon": (156, 194, 191),  # dark cyan
                     "rare": (0, 255, 0),  # Green
                     "epic": (128, 0, 128),  # Purple
                     "legendary": (255, 0, 0)  # Red
                     }

    @staticmethod
    def generate_upgrade(game, width, height, font):
        filtered_options = [option for option in Upgrade.upgrade_options if option['weight'] > 0]
        options = []
        num_options = random.randint(2, min(3 + game.player.lvl // 20, 6))

        while len(options) != num_options:
            option = random.choices(filtered_options, weights=[option['weight'] for option in filtered_options], k=1)[0]
            if option['name'] != "None":
                options.append(option)

        chosen_upgrade = Upgrade.draw_upgrade_menu(game.screen, width, height, font, options)

        if chosen_upgrade:
            Upgrade.apply_upgrade(game, chosen_upgrade['name'])

    @staticmethod
    def apply_upgrade(game, choice):
        player = game.player
        if choice == "Tougher Bullets":
            player.bullet_size += 1
            player.dmg += 1
            player.bullet_color = tuple(random.choices(range(256), k=3))

        elif choice == "Faster Shooting":
            player.fire_rate = max(1, player.fire_rate * 0.7)
        elif choice == "More Bullets":
            player.bullet_amount += 1
        elif choice == "Better Pierce":
            player.pierce_lvl += 1
            Upgrade.disable_upgrade(player, 'Fork Bullet')
        elif choice == "Fork Bullet":
            player.fork_lvl += 1
            if player.fork_lvl == 5:
                Upgrade.disable_upgrade(player, 'Fork Bullet')
            Upgrade.disable_upgrade(player, 'Better Pierce')
        elif choice == "Shield":
            player.shield_lvl += 1
            player.shield_size += [0.15, 0.2, 0.25][player.shield_lvl - 1]
            if player.shield_lvl == 3:
                Upgrade.disable_upgrade(player, 'Shield')

        elif choice == "Increased Max Health":
            player.max_health = int(1.5 * player.max_health)
            player.health = player.max_health
            player.size += 2

        elif choice == "Faster Movement":
            player.speed += 1
            if player.size > 5:
                player.size -= 1

        elif choice == "Magnet Drops":
            player.magnet_lvl += 1
            if player.magnet_lvl == 2:
                Upgrade.disable_upgrade(player, 'Magnet Drops')

        elif choice == "Energy Pulse":
            player.energy_pulse_lvl += 1
            player.energy_pulse_timer = pygame.time.get_ticks()
            if player.energy_pulse_lvl == 3:
                Upgrade.disable_upgrade(player, 'Energy Pulse')

        elif choice == "Omnivamp":
            player.omnivamp_lvl += 1

        elif choice == "Spread Shot":
            player.spreadShot = True
            Upgrade.disable_upgrade(player, 'Spread Shot')

        elif choice == "Spinning Swords":
            for i in range(3):
                angle = i * (2 * math.pi / 3)
                x = player.pos[0] + 70 * math.cos(angle)
                y = player.pos[1] + 70 * math.sin(angle)
                game.summons.append(Summon([x,y], angle, "spinning_sword"))

            Upgrade.disable_upgrade(player, 'Spinning Swords')

        elif choice == "Healer":
            angle = random.uniform(0, 2 * math.pi)
            x = player.pos[0] + 30 * math.cos(angle)
            y = player.pos[1] + 30 * math.sin(angle)
            game.summons.append(Summon([x,y], 0, "healer"))

            Upgrade.disable_upgrade(player, 'Healer')

    @staticmethod
    def disable_upgrade(player, upgrade):
        player.disabled_upgrades.append(upgrade)

        weight_to_add = 0
        for option in Upgrade.upgrade_options:
            if option["name"] == upgrade:
                weight_to_add = option["weight"]
                option["weight"] = 0
        for option in Upgrade.upgrade_options:
            if option["name"] == "None":
                option["weight"] += weight_to_add

    @staticmethod
    def draw_upgrade_menu(screen, width, height, font, options):
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(192)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_text = font.render("Level Up! Choose an upgrade:", True, (255, 255, 255))
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 4))

        for i, option in enumerate(options):
            option_text = font.render(f"{i + 1}. {option['name']}", True, Upgrade.rarity_colors[option['rarity']])
            screen.blit(option_text, (width // 2 - option_text.get_width() // 2, height // 2 + i * 50))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6][:len(options)]:
                        return options[event.key - pygame.K_1]
        return None
