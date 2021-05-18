import cv2
from screen import Screen
from os import listdir
from os.path import isfile, join

def read_level_images(folder, num_levels, screen_height, steering_img_ratio):
    path = "assets/levels/{}".format(folder)
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.sort()
    images = []
    for i in range(min(num_levels, len(files))):
        img = cv2.imread("assets/levels/{}/{}".format(folder, files[i]), -1)
        img = cv2.resize(img, (int(screen_height * steering_img_ratio),
                               (screen_height)))
        img = Screen.cvimage_to_pygame(img)
        images.append(img)
    return images

