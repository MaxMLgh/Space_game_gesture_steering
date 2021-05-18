import pygame

# every object on the screen
class Space_Objects:
    def __init__(self, x=0, y=0, size=50, img="battleship.png", sound=None):
        self.x = x 
        self.y = y
        self.size = size
        self.img = pygame.image.load("assets/" + img)
        self.img = pygame.transform.scale(self.img, (self.size, self.size))
        if sound is not None:
            self.sound = pygame.mixer.Sound("assets/" + sound)
        else:
            self.sound = None
        
    def detect_collision(self, other):
        if (other.x+other.size>=self.x and other.x<=(self.x + self.size)) and \
                (other.y+other.size>=self.y and other.y<=(self.y + self.size)):
            return True
        return False

# spaceship that player pilot
class Player(Space_Objects):    
    def __init__(self, x=0, y=0, size=80, img="battleship.png", sound="explosion.wav"):
        super().__init__(x, y, size, img, sound)
        self.y = y - self.size

# laser destroys any object
class Laser(Space_Objects):
    player_basic_size = 120
    def __init__(self, player_x=0, player_y=0, player_size=0, size=60,
                 img="laser_2.png", sound="laser_2.wav"):
        self.size = int(size * player_size/self.player_basic_size)
        self.x = player_x + int(0.5*(player_size - self.size))
        self.y = player_y - int(self.size)
        self.img = pygame.image.load("assets/" + img)
        self.img = pygame.transform.scale(self.img, (self.size, self.size))
        if sound is not None:
            self.sound = pygame.mixer.Sound("assets/" + sound)
        else:
            self.sound = None
    
# collision with those objects can change life and score
class Resources_Obstacles(Space_Objects):
    def __init__(self, x=0, y=0, size=50, img="battleship.png",
                 sound="explosion.wav", life=0, score=0, game_screen_width=1000):
        super().__init__(x, y, size, img, sound)
        # how collision affect life and points of a player
        self.life = life
        self.score = score