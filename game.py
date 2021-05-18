import random
import pygame
from screen import Color
from space_objects import Resources_Obstacles, Laser

class Game:
    basic_screen_size = 1000
    basic_FPS = 20
    resources_obstacles =[ 
            {"img":"comet.png", "sound":"explosion.wav", "size":100, "life":-20,
             "score":0, 'probability': 0.5},
            {"img":"empire_ship.png", "sound":"explosion.wav", "size":80, "life":-15,
             "score":0, 'probability': 0.3},
            {"img": "ufo.png", "sound": "explosion.wav", "size": 80,
             "life": -25,  "score": 0, 'probability': 0.2},
            {"img":"diamond.png", "sound":"point.wav", "size":60, "life":0,
             "score":20, 'probability': 0.4},
            {"img": "red_diamond.png", "sound": "point.wav", "size": 50, "life": 0,
             "score": 30, 'probability': 0.2},
            {"img": "gold_diamond.png", "sound": "point.wav", "size": 50, "life": 0,
             "score": 50, 'probability': 0.05},
            {"img": "tools.png", "sound": "tools.wav", "size": 60, "life": 10,
             "score": 0, 'probability': 0.2}
        ]
    
    def __init__(self, sound=False, n_levels=100, initial_speed=10, speed_jump=2,
                 max_speed=100, pnt_next_lvl=50, game_screen_height=1000,
                 game_screen_width=1000):
        self.game_screen_height = game_screen_height
        self.game_screen_width =game_screen_width
        self.sound = sound
        self.n_levels = n_levels
        self.initial_speed = initial_speed * self.game_screen_height / self.basic_screen_size
        self.speed_jump = speed_jump * self.game_screen_height / self.basic_screen_size
        self.max_speed = max_speed * self.game_screen_height / self.basic_screen_size
        self.pnt_nex_lvl = pnt_next_lvl
        self.life = 100
        self.score = 0
        self.speed = self.initial_speed
        self.level = 1
        self.ammunition = 10
        self.resources_obstacles_list = []
        self.laser_list = []
        self.level_images = None
        self.FPS = 20
        self.name_player = ""
        self.record_names, self.record_scores = self.read_records()
        self.player_index_records = None
        sum_of_probabilities = sum(
            [object['probability'] for object in self.resources_obstacles])
        self.probability_of_objects = [
            object['probability'] / sum_of_probabilities for object in
            self.resources_obstacles]
        if sound:
            background_sound = "background_2.wav"
            pygame.mixer.music.load('assets/{}'.format(background_sound))
            pygame.mixer.music.play(-1)

    def read_records(self):
        with open("assets/records.txt", 'r') as f:
            records = f.readlines()
        record_names = [''.join(line.split()[:-1]) for line in records]
        record_scores = [int(line.split()[-1]) for line in records]
        return record_names, record_scores

    """
    Function creates objects 'above' the game screen. With every iteration game lowers them down
    number of pixels equal to Game.speed. When aggregated number of passed pixels surpass or equals to 
    height of the screen function is reapeted.
    """
    def create_resources_obstacles(self, screen_width, screen_height):
        resources_obstacles_number = random.randint(3+self.level, 10+self.level)
        for i in range(resources_obstacles_number):
            # parameters of new objects of Obstacles_Resources
            ro_param = random.choices(self.resources_obstacles, self.probability_of_objects)[0]            
            ro_x = random.randint(0, screen_width)
            ro_y = random.randint(-screen_height, 0)
            size = int(ro_param["size"] * self.game_screen_width / self.basic_screen_size)
            new_ro = Resources_Obstacles(x=ro_x, y=ro_y,
                                    img=ro_param["img"],sound=ro_param["sound"],
                                    size=size,life=ro_param["life"],
                                    score=ro_param["score"])
            self.resources_obstacles_list.append(new_ro)

    def create_laser(self, player_x, player_y, player_size):
        if self.ammunition >= 1:
            laser = Laser(player_x, player_y, player_size)
            self.laser_list.append(laser)
            self.ammunition -= 1
            if laser.sound is not None and self.sound:
                laser.sound.play()


    def update_resources_obstacles_positions(self, screen_height):
        for ro in self.resources_obstacles_list:
            if ro.y < screen_height:
                ro.y += self.speed
            else:
                self.resources_obstacles_list.remove(ro)

    def update_lasers_positions(self, pixels):
        for laser in self.laser_list:
            if laser.y > 0:
                laser.y -= self.speed
            else:
                self.laser_list.remove(laser)
                            
    def set_level_and_speed(self):
        level = min(int(1 + self.score/self.pnt_nex_lvl), self.n_levels, len(self.level_images))
        if level > self.level and self.sound:
            pygame.mixer.Sound("assets/level.wav").play()
        self.level = level
        self.speed = min((self.initial_speed + self.level * self.speed_jump) * self.basic_FPS / self.FPS,
                         self.max_speed)

    def collision_check(self, player):
        for ro in self.resources_obstacles_list:
            if ro.detect_collision(player):
                self.life = min(self.life+ro.life, 100)
                self.score += ro.score
                self.resources_obstacles_list.remove(ro)
                if ro.sound is not None and self.sound:
                    ro.sound.play()

    def laser_hit_check(self):
        for laser in self.laser_list:
            for ro in self.resources_obstacles_list:
                if ro.detect_collision(laser):
                    self.resources_obstacles_list.remove(ro)
                    self.laser_list.remove(laser)
                    if ro.sound is not None and self.sound:
                        ro.sound.play()
                    break

    def find_player_index_records(self):
        index = 'Not in records'
        for i in reversed(range(len(self.record_scores))):
            if self.score > self.record_scores[i]:
                index = i
        print(index)
        self.player_index_records = index

    # function that is run after player have lost
    def end_game(self, screen, game, img):
        if self.player_index_records is None:
            game.find_player_index_records()
        screen.refresh_background()
        screen.draw_level_img(game.level, game.level_images)
        screen.draw_steering_img(img)
        screen.draw_corner_text(f"Level: {game.level}", screen.width + 5, 0,
                              color=Color.RED, font_size=50)
        screen.draw_centered_text(text="YOU LOST!", x=0.5*screen.width, y=0.2*screen.height,
                         color=Color.RED, font_type="cambria", font_size=80)
        screen.draw_centered_text(text=f"YOUR SCORE: {game.score}", x=0.5*screen.width,
                                  y=0.3*screen.height,
                         color=Color.RED, font_type="cambria", font_size=50)
        screen.draw_centered_text(text=f"Press LEFT CTRL to start again", x=0.5*screen.width,
                                  y=0.8*screen.height,
                         color=Color.GREEN, font_type="cambria", font_size=50)
        screen.draw_centered_text(text=f"Press ESCAPE to end game", x=0.5*screen.width,
                                  y=0.9*screen.height,
                         color=Color.GREEN, font_type="cambria", font_size=50)


        if self.player_index_records!='Not in records':
            self.record_names[self.player_index_records] = self.name_player
            self.record_scores[self.player_index_records] = game.score

            screen.draw_centered_text(text=f"TYPE YOUR NAME AND PRESS ENTER", x=0.5 * screen.width,
                                      y=0.4 * screen.height,color=Color.RED, font_type="cambria",
                                      font_size=40)

            for i in range(len(self.record_scores)):
                screen.draw_centered_text(text=f"{i+1}. {self.record_names[i]}: {self.record_scores[i]}",
                                          x=0.5 * screen.width, y=(0.5+0.05*i) * screen.height,
                                          color=Color.RED, font_type="cambria", font_size=40)

            for event in pygame.event.get():
                if event == pygame.QUIT:
                    return 'over'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(self.name_player) > 0:
                            with open("assets/" + 'records.txt', 'w') as file:
                                for i in range(len(self.record_scores)):
                                    file.write(f"{self.record_names[i]} {self.record_scores[i]}\n")
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_player = self.name_player[:-1]
                    elif event.key == pygame.K_LCTRL:
                        return 'new game'
                    elif event.key == pygame.K_ESCAPE:
                        return 'over'
                    else:
                        if len(self.name_player) < 15:
                            self.name_player += event.unicode.upper()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'over'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        return 'new game'
                    elif event.key == pygame.K_ESCAPE:
                        return 'over'
