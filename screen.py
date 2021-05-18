import pygame
import cv2
import math
import time

class Color:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)

class Screen:
    basic_screen_size = 1000

    def __init__(self, width=1000, height=1000, font_type="cambria",
                 font_size=35, background="space.jpg", steering_img_ratio=1,
                 wheel_img_original='wheel_2.png', arrow_img='arrow_direction.png',
                 gun_img='space-gun.png'):
        self.width = width
        self.height = height
        self.steering_img_width = int(0.5 * self.height * steering_img_ratio)
        self.steering_img_height = int(0.5 * self.height)
        self.wheel_img_original = pygame.image.load("assets/" + wheel_img_original)
        self.arrow_right_img = pygame.image.load("assets/" + arrow_img)
        self.arrow_left_img = pygame.transform.flip(self.arrow_right_img, True, False)
        gun_img = pygame.image.load("assets/" + gun_img)
        self.gun_img = pygame.transform.scale(gun_img, (int(self.height * 0.2),
                                                        int(self.height * 0.2)))
        self.screen = pygame.display.set_mode((width + self.steering_img_width, height))
        self.font = pygame.font.SysFont(font_type, font_size)
        self.background = pygame.image.load("assets/" + background)
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

    def refresh_background(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0,0))
    
    def draw_resources_obstacles(self, resources_obstacles_list):
        for ro in resources_obstacles_list:
            self.screen.blit(ro.img, (ro.x, ro.y))

    def draw_laser(self, laser_list):
        for laser in laser_list:
            self.screen.blit(laser.img, (laser.x, laser.y))

    def draw_player(self, player):
        self.screen.blit(player.img, (player.x, player.y))

    # x, y are coordinates of left, upper corner of text
    def draw_corner_text(self, text, x, y, color=Color.RED, font_type="cambria", font_size=35):
        font_size = int(font_size * self.width / self.basic_screen_size)
        font = pygame.font.SysFont(font_type, font_size)
        label = font.render(text, 1, color)
        self.screen.blit(label, (x, y))

    # x, y are coordinates of center of text
    def draw_centered_text(self, text, x, y, color=Color.RED, font_type="cambria", font_size=35):
        font_size = int(font_size * self.width / self.basic_screen_size)
        font = pygame.font.SysFont(font_type, font_size)
        label = font.render(text, 1, color)
        label_rect = label.get_rect(center=(x, y))
        self.screen.blit(label, label_rect)

    def cvimage_to_pygame(image):
        return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")


    def draw_level_img(self, level, level_images):
        self.screen.blit(
            level_images[min(level - 1, len(level_images) - 1)],
            (self.width, 0))


    def draw_steering_img(self, img):
        img = cv2.resize(img,
                         (self.steering_img_width, int(self.height * 0.5)))
        img = Screen.cvimage_to_pygame(img)
        self.screen.blit(img, (self.width, int(0.5 * self.height)))


    def draw_wheel(self, steering):
        if steering.wheel_angle is None:
            return
        wheel_img = self.wheel_img_original.copy()
        wheel_img = pygame.transform.rotate(wheel_img, steering.wheel_angle)
        """ When rotating the squared image, new square that contains rotated image may grow.
          Corners of the square rotated (e.g. 20 degree) spreads more that the flat one."""
        scale = math.cos(math.radians(steering.wheel_angle % 45))/math.cos(math.radians(45))
        radius = int(abs(1 * steering.wheel_radius * scale))
        wheel_img = pygame.transform.scale(wheel_img, (2 * radius, 2 * radius))
        wheel_x = self.width + steering.wheel_center[0] - radius
        wheel_y = self.steering_img_height + steering.wheel_center[1] - radius
        self.screen.blit(wheel_img, (wheel_x, wheel_y))
        #pygame.draw.circle(self.screen, (0,255,0), (wheel_x, wheel_y), 10, 10)


    def draw_arrow(self, steering):
        if steering.wheel_angle is None:
            return 0

        if steering.turn > 0:
            arrow_img = self.arrow_right_img.copy()
        else:
            arrow_img = self.arrow_left_img.copy()

        size = abs(int(steering.turn * 0.003 * self.width))
        arrow_img = pygame.transform.scale(arrow_img, (size, size))

        if steering.turn > 0:
            self.screen.blit(arrow_img, (self.width, self.steering_img_height))
        else:
            self.screen.blit(arrow_img, (self.width + self.steering_img_width - size,
                                         self.steering_img_height))


    def draw_gun(self, steering):
        if time.time() - steering.shot_pause_time > 0.2:
            return
        else:
            self.screen.blit(self.gun_img, (self.width, int(1.3 * self.steering_img_height)))


    def update_screen(self, game, player, img, steering, start_time):
        self.refresh_background()
        self.draw_resources_obstacles(game.resources_obstacles_list)
        self.draw_laser(game.laser_list)
        self.draw_player(player)
        self.draw_corner_text(f"Score: {game.score}", 0, int(0.04*self.width),
                              color=Color.RED)
        self.draw_corner_text(f"Life: {game.life}", 0, int(0.08*self.width),
                              color=Color.RED)
        self.draw_corner_text(f"Amo: {game.ammunition}", 0, int(0.12*self.width),
                              color=Color.RED)
        self.draw_steering_img(img)
        self.draw_wheel(steering)
        self.draw_arrow(steering)
        self.draw_gun(steering)
        self.draw_level_img(game.level, game.level_images)
        self.draw_corner_text(f"Level: {game.level}", self.width + 5, 0,
                              color=Color.RED, font_size=50)
        self.draw_corner_text(f"FPS: {round(1/(time.time()- start_time))}", 0, 0,
                              color=Color.RED, font_size=35)
