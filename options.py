import pygame


class Options:
    current_resolution_index = 2

    def __init__(self, game):
        self.game = game
        self.in_options_menu = False
        self.fullscreen = False
        self.resolutions = [(800, 600), (1280, 720), (1920, 1080), (2560, 1440)]

        self.font = pygame.font.Font(None, 40)

        self.change_resolution_height = 150
        self.resolutions_height = 170
        self.fullscreen_height = 250
        self.back_height = 350

    def draw_options_menu(self):
        screen = self.game.screen
        WIDTH, HEIGHT = self.resolutions[Options.current_resolution_index]

        title_font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 34)
        screen.fill((0, 0, 0))

        title_text = title_font.render("Options", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        change_res_text = self.font.render("Change Resolution", True, (255, 255, 255))
        change_res_rect = change_res_text.get_rect(center=(WIDTH // 2, self.change_resolution_height))
        screen.blit(change_res_text, change_res_rect)

        resolution_text = small_font.render(f"(Resolution: {WIDTH}x{HEIGHT})", True, (255, 255, 255))
        screen.blit(resolution_text, (WIDTH // 2 - resolution_text.get_width() // 2, self.resolutions_height))

        fullscreen_text = self.font.render(f"Fullscreen: {'On' if self.fullscreen else 'Off'}", True, (255, 255, 255))
        fullscreen_rect = fullscreen_text.get_rect(center=(WIDTH // 2, self.fullscreen_height))
        screen.blit(fullscreen_text, fullscreen_rect)

        back_text = self.font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(WIDTH // 2, self.back_height))
        screen.blit(back_text, back_rect)

    def change_resolution(self):
        Options.current_resolution_index = (Options.current_resolution_index + 1) % len(self.resolutions)
        new_width, new_height = self.resolutions[Options.current_resolution_index]

        if not self.fullscreen:
            self.game.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            self.game.WIDTH = new_width
            self.game.HEIGHT = new_height

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        WIDTH, HEIGHT = self.resolutions[Options.current_resolution_index]

        if self.fullscreen:
            self.game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.game.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    def handle_options_click(self, pos):
        WIDTH = self.resolutions[Options.current_resolution_index][0]

        change_res_rect = self.font.render("Change Resolution", True, (255, 255, 255)).get_rect(
            center=(WIDTH // 2, self.change_resolution_height))
        fullscreen_rect = self.font.render(f"Fullscreen: {'On' if self.fullscreen else 'Off'}", True,
                                      (255, 255, 255)).get_rect(center=(WIDTH // 2, self.fullscreen_height))
        back_rect = self.font.render("Back", True, (255, 255, 255)).get_rect(center=(WIDTH // 2, self.back_height))

        if change_res_rect.collidepoint(pos):
            self.change_resolution()
        elif fullscreen_rect.collidepoint(pos):
            self.toggle_fullscreen()
        elif back_rect.collidepoint(pos):
            self.game.screen.fill((0, 0, 0))
            self.in_options_menu = False
