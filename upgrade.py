import pygame
import math
import random

from pickup import Pickup
from summon import Summon


class Upgrade:
    upgrade_options_legendary = ["Wizard", "Homing Bullets"]
    upgrade_options_epic = ["Magnet Drops", "Energy Pulse", "Omnivamp", "Spread Shot", "Healer",
                            "Robo Helper"]
    upgrade_options_rare = ["More Bullets", "Better Pierce", "Fork Bullet", "Spinning Swords"]
    upgrade_options_uncommon = ["Shield", "Faster Shooting", "Damage Increase", "Freezing Bullets", "Burning Bullets"]
    upgrade_options_common = ["Increased Max Health", "Faster Movement", "More Ammo on Pickup", "Faster Bullets"]

    rarity_rates = {"common": 35, "uncommon": 30, "rare": 25, "epic": 8, "legendary": 2}

    rarity_colors = {"common": (255, 255, 255),  # White
                     "uncommon": (156, 194, 191),  # Green
                     "rare": (0, 235, 235),  # Cyan
                     "epic": (228, 0, 228),  # Purple
                     "legendary": (255, 0, 0)  # Red
                     }

    @staticmethod
    def generate_upgrade(game, width, height, font):
        options = []
        num_options = random.randint(2, min(3 + game.player.lvl // 20, 6))

        while len(options) != num_options:
            option = None
            rarity_class = random.choices(list(Upgrade.rarity_rates.keys()), weights=list(Upgrade.rarity_rates.values()))[0]
            if rarity_class == "common":
                option = random.choice(Upgrade.upgrade_options_common)
            elif rarity_class == "uncommon":
                option = random.choice(Upgrade.upgrade_options_uncommon)
            elif rarity_class == "rare":
                option = random.choice(Upgrade.upgrade_options_rare)
            elif rarity_class == "epic":
                option = random.choice(Upgrade.upgrade_options_epic)
            elif rarity_class == "legendary":
                option = random.choice(Upgrade.upgrade_options_legendary)

            if option:
                options.append((option, rarity_class))

        chosen_upgrade = Upgrade.draw_upgrade_menu(game.screen, width, height, font, options)

        if chosen_upgrade:
            Upgrade.apply_upgrade(game, chosen_upgrade)

    @staticmethod
    def apply_upgrade(game, choice):
        player = game.player

        # legendary
        if choice == "Wizard":
            player.proj_type = "lightning"
            player.dmg += 5
            player.fire_rate *= 3
            Upgrade.disable_upgrade(choice)

        elif choice == "Homing Bullets":
            player.proj_type = "homing"
            Upgrade.disable_upgrade(choice)

        # epic
        elif choice == "Magnet Drops":
            player.magnet_lvl += 1
            if player.magnet_lvl == 2:
                Upgrade.disable_upgrade(choice)

        elif choice == "Energy Pulse":
            player.energy_pulse_lvl += 1
            player.energy_pulse_timer = pygame.time.get_ticks()
            if player.energy_pulse_lvl == 3:
                Upgrade.disable_upgrade("Energy Pulse")

        elif choice == "Omnivamp":
            player.omnivamp_lvl += 1
            Upgrade.disable_upgrade(choice)

        elif choice == "Spread Shot":
            player.spreadShot = True
            Upgrade.disable_upgrade(choice)

        elif choice in ["Healer", "Robo Helper"]:
            game.summons.append(Summon(player.pos, 0, choice.lower()))

            if choice == "Robo Helper":
                player.ammo += 50
            elif choice == "Healer":
                player.health = min(game.player.health * 1.3, game.player.max_health)

            Upgrade.disable_upgrade(choice)

        elif choice == "Magic Shield":
            player.magic_shield = True

        # rare
        elif choice == "More Bullets":
            player.bullet_amount += 1

        elif choice == "Better Pierce":
            player.pierce_lvl += 1
            if player.pierce_lvl == 5:
                player.bullet_shape = "line"
                Upgrade.disable_upgrade(choice)
            Upgrade.disable_upgrade("Fork Bullet")

        elif choice == "Fork Bullet":
            player.fork_lvl += 1
            if player.fork_lvl == 5:
                Upgrade.disable_upgrade(choice)
            Upgrade.disable_upgrade("Better Pierce")

        elif choice == "Spinning Swords":
            for i in range(3):
                angle = i * (2 * math.pi / 3)
                x = player.pos[0] + 70 * math.cos(angle)
                y = player.pos[1] + 70 * math.sin(angle)
                game.summons.append(Summon([x,y], angle, choice.lower()))

            Upgrade.upgrade_options_rare.append("Enchanted Sword")
            Upgrade.disable_upgrade(choice)

        elif choice == "Enchanted Sword":
            game.summons.append(Summon(player.pos, 0, choice.lower()))

        # uncommon
        elif choice == "Damage Increase":
            player.dmg += 1
            player.bullet_color = tuple(random.choices(range(150, 256), k=3))

        elif choice == "Faster Shooting":
            player.fire_rate = max(1, player.fire_rate * 0.7)

        elif choice == "Shield":
            player.shield_lvl += 1
            player.shield_size += [0.15, 0.2, 0.25][player.shield_lvl - 1]
            if player.shield_lvl == 3:
                Upgrade.disable_upgrade(choice)
                Upgrade.upgrade_options_epic.append("Magic Shield")

        elif choice == "Freezing Bullets":
            player.bullet_dot = "freeze"
            Upgrade.disable_upgrade(choice)
            if "Burning Bullets" not in Upgrade.upgrade_options_uncommon:
                Upgrade.upgrade_options_uncommon.append("Burning Bullets")

        elif choice == "Burning Bullets":
            player.bullet_dot = "burn"
            Upgrade.disable_upgrade(choice)
            if "Freezing Bullets" not in Upgrade.upgrade_options_uncommon:
                Upgrade.upgrade_options_uncommon.append("Freezing Bullets")

        # common
        elif choice == "Increased Max Health":
            player.max_health = int(1.5 * player.max_health)
            player.health = player.max_health

        elif choice == "Faster Movement":
            player.max_speed += 1
            player.speed = player.max_speed

        elif choice == "More Ammo on Pickup":
            player.ammo += 25
            Pickup.ammo_upgrade_bonus += 10

        elif choice == "Faster Bullets":
            player.bullet_speed *= 1.1

    @staticmethod
    def disable_upgrade(upgrade):
        if upgrade in Upgrade.upgrade_options_legendary:
            Upgrade.upgrade_options_legendary.remove(upgrade)
        elif upgrade in Upgrade.upgrade_options_epic:
            Upgrade.upgrade_options_epic.remove(upgrade)
        elif upgrade in Upgrade.upgrade_options_rare:
            Upgrade.upgrade_options_rare.remove(upgrade)
        elif upgrade in Upgrade.upgrade_options_uncommon:
            Upgrade.upgrade_options_uncommon.remove(upgrade)
        elif upgrade in Upgrade.upgrade_options_common:
            Upgrade.upgrade_options_common.remove(upgrade)
    @staticmethod
    def draw_upgrade_menu(screen, width, height, font, options):
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(192)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_text = font.render("Level Up! Choose an upgrade:", True, (255, 255, 255))
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 4))

        clock = pygame.time.Clock()
        animation_time = 0

        waiting = True
        while waiting:
            screen.blit(overlay, (0, 0))
            screen.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 4))

            for i, (option, rarity) in enumerate(options):
                color = Upgrade.rarity_colors[rarity]

                # Pulsating effect for rare and higher upgrades
                if rarity == "legendary":
                    # Rainbow effect for legendary rarity
                    hue = (animation_time / 10) % 360
                    color = pygame.Color(0)
                    color.hsva = (hue, 100, 100, 100)

                if rarity in ["rare", "epic"]:
                    scale = 1.0 + 0.2 * math.sin(animation_time / 100.0)
                    # Ensure each color channel is clamped between 0 and 255
                    scaled_color = tuple(max(0, min(255, int(c * scale))) for c in color)
                else:
                    scaled_color = color

                option_text = font.render(f"{i + 1}. {option}", True, scaled_color)
                screen.blit(option_text, (width // 2 - option_text.get_width() // 2, height // 2 + i * 50))

            pygame.display.flip()
            clock.tick(60)
            animation_time += clock.get_time() / 2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6][
                                    :len(options)]:
                        return options[event.key - pygame.K_1][0]

        return None
