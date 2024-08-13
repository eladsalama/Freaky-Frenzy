import pygame

class Background:
    def __init__(self, world_map_path, width, height):
        self.width = width
        self.height = height

        self.image = pygame.image.load(world_map_path).convert()
        self.rect = self.image.get_rect()

        self.scaled_subsurface = None
        self.blit_x = 0
        self.blit_y = 0

        # Variables to hold previous items
        self.prev_camera_pos = width // 2, height // 2
        self.prev_zoom = None
        self.map_view = None
        self.last_update_time = pygame.time.get_ticks()
        self.update_interval = 10

    def draw(self, screen, camera):
        current_time = pygame.time.get_ticks()

        # Only update the world map movement at the specified frame rate
        if (current_time - self.last_update_time >= self.update_interval or not self.scaled_subsurface) \
                and (self.prev_camera_pos != camera.pos or self.prev_zoom != camera.zoom):

            cam_x, cam_y = camera.pos
            zoom = camera.zoom

            # Cache calculations for view dimensions
            view_width = int(self.width / zoom)
            view_height = int(self.height / zoom)
            half_width = view_width / 2
            half_height = view_height / 2

            # Calculate the view's position in the background's coordinate system
            view_left = int(cam_x - half_width)
            view_top = int(cam_y - half_height)

            # Ensure the view stays within the background bounds
            view_left = max(0, min(view_left, self.rect.width - view_width))
            view_top = max(0, min(view_top, self.rect.height - view_height))

            # Calculate the portion of the background to draw
            bg_rect = pygame.Rect(view_left, view_top,
                                  min(view_width, self.rect.width - view_left),
                                  min(view_height, self.rect.height - view_top))

            # Create a subsurface of the background image
            subsurface = self.image.subsurface(bg_rect)

            scaled_size = (int(bg_rect.width * zoom), int(bg_rect.height * zoom))
            self.scaled_subsurface = pygame.transform.scale(subsurface, scaled_size)

            # Calculate the position to blit the background
            self.blit_x = int((view_left - cam_x) * zoom + self.width / 2)
            self.blit_y = int((view_top - cam_y) * zoom + self.height / 2)

            # Update previous state variables
            self.last_update_time = current_time
            self.prev_camera_pos = camera.pos[:]
            self.prev_zoom = zoom

        # Draw the scaled subsurface if it exists
        if self.scaled_subsurface:
            screen.blit(self.scaled_subsurface, (self.blit_x, self.blit_y))
