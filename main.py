import sys
import time
import pygame
import cv2
import argparse
from win32api import GetSystemMetrics
from steering import HandDetector, Steering
from space_objects import Player
from screen import Screen
from game import Game
from level_images_load import read_level_images


def play_game():
    vid = cv2.VideoCapture(args.camera)
    vid_h = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    vid_w = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    steering_img_ratio = vid_w / vid_h

    game_screen_height = args.height
    game_screen_width = args.width
    steering_screen_height = int(game_screen_height * 0.5)
    steering_screen_width = int(steering_screen_height * steering_img_ratio)
    detector = HandDetector(steering_screen_height, steering_screen_width,
                            static_image_mode=args.static_image_mode,
                            detection_confidence=args.detection_confidence,
                            tracking_confidence=args.tracking_confidence,
                            draw_hands=False)

    pygame.init()
    screen = Screen(width=game_screen_width, height=game_screen_height,
                    steering_img_ratio=steering_img_ratio)
    player = Player(x=screen.width / 2, y=screen.height , size=int(0.1 * game_screen_width))
    game = Game(game_screen_height=game_screen_height, game_screen_width=game_screen_width,
                initial_speed=args.initial_speed, speed_jump=args.speed_jump,
                pnt_next_lvl=args.pnt_next_lvl, sound=args.sound)
    game.level_images = read_level_images(args.folder_levels, game.n_levels,
                                          steering_screen_height, steering_img_ratio)
    steering = Steering(steering_screen_height, steering_screen_width)

    # how many pixel passed
    pixels = 0
    previous_pixel_count = 1
    while True:
        start_time = time.time()
        _, img_full_size = vid.read()
        img_full_size = cv2.flip(img_full_size, 1)
        img = cv2.resize(img_full_size, (steering_screen_width, steering_screen_height))

        if game.life > 0:
            detector.get_hands_params(img_full_size)
            steering.calculate_wheel(img, detector.left_hand,
                                     detector.right_hand)
            if steering.wheel_radius is not None:
                turn, shot = steering.get_commands(detector)
            else:
                turn = None
                shot = False

            game.collision_check(player)
            game.laser_hit_check()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    vid.release()
                    sys.exit()
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        vid.release()
                        play_game()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        pygame.quit()
                        vid.release()
                        sys.exit()
                        break

            if turn is not None:
                player.x = min(max(player.x - 0.002 * steering.wheel_angle * player.size, 0),
                               screen.width - player.size)
            if shot:
                game.create_laser(player.x, player.y, player.size)

            # when to create new resources and obstacles
            """ We create new space objects 'above' the screen every time,
             that the previous screen have passed, lets say speed = 4,
             so previous_pixel_count 2998 % 1000 = 998,
             but current_pixel_count 3002 % 1000 = 2 , 2 < 998,
             but the next one will be 3006 % 1000 = 6, 6 > 2,
             so only once when screen passes we create new objects."""
            current_pixel_count = pixels % screen.height
            if current_pixel_count < previous_pixel_count:
                game.create_resources_obstacles(screen.width, screen.height)
                game.ammunition = min(game.ammunition + 2, 10)
            previous_pixel_count = current_pixel_count
            pixels += game.speed

            game.update_resources_obstacles_positions(screen.height)
            game.update_lasers_positions(pixels)
            game.set_level_and_speed()
            screen.update_screen(game, player, img, steering, start_time)
            pygame.display.update()
        else:
            pygame.display.update()

            game_state = game.end_game(screen, game, img)
            if game_state == 'over':
                pygame.display.quit()
                pygame.quit()
                vid.release()
                sys.exit()
                break
            elif game_state == 'new game':
                vid.release()
                play_game()
        game.FPS = 1/(time.time() - start_time)

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--height', type=int, default=int(GetSystemMetrics(1)-100),
                        help='height of game window')
    parser.add_argument('--width', type=int, default=int(GetSystemMetrics(1)-100),
                        help='width of game window')
    parser.add_argument('--camera', type=int, default=0,
                        help='which camera')
    parser.add_argument('--folder_levels', type=str, default='star_wars',
                        help='level images folder')
    parser.add_argument('--initial_speed', type=float, default=8,
                        help='initial speed')
    parser.add_argument('--speed_jump', type=float, default=1.5,
                        help='speed jump when next level')
    parser.add_argument('--pnt_next_lvl', type=int, default=100,
                        help='how many points to achieve next level')
    parser.add_argument('--sound', type=str2bool, nargs='?',
                        const=True,  default='False', help='sounds of the game')
    parser.add_argument('--detection_confidence', type=float, default=0.4,
                        help='detection confidence')
    parser.add_argument('--tracking_confidence', type=float, default=0.3,
                        help='tracking confidence')
    parser.add_argument('--static_image_mode', type=str2bool, nargs='?',
                        const=True, default='False',
                        help='treat frames as separate images, not video')
    args = parser.parse_args()
    play_game()