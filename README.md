# Star Wars

Star Wars is a game implemented in **PYTHON** library **Pygame**. To steer the spaceship we use **Mediapipe**, which is a library that uses **Artificial Intelligence** to recognize and map the positions of the points on your hands.  
Link to **Youtube** video:  
https://www.youtube.com/watch?v=If5fU0IgPDw&t=517s  
Our goal is to collect as many points as we can, you collect them by catching gems. You also have to look for asteroids and enemy spaceships, you can simply run from them or shoot them with a laser. If they hit you you will lose life points, you can restore them by catching tools. With more points, objects are appearing with higher velocity. 
To steer the spaceship you need to pretend that you are holding a wheel, like you would do while driving a car. 
The stronger you turn, the faster the spaceship will turn. You shoot laser by giving the thumbs up with both of your hands, while the rest of the fingers are folded.
If you'll be a good enough pilot you can cover yourself with glory and earn places in the ranks of 5 the best pilots in the galaxy!!!
 ## Demo of a game
![sg](https://user-images.githubusercontent.com/73268650/118136149-13ccf480-b404-11eb-81db-224dae58101e.gif)
## Tips for better steering:
1. Make sure your hands are visible for the camera.
2. Make sure you have a good lighting and the camera sees you clearly.
3. Try to avoid rapid movements of hands, so they wouldn't look blurry for the camera.
4. Try to remember to keep your hands in fist positions (fingers folded).

## How to shoot and steer.
![image](https://user-images.githubusercontent.com/84282532/118842798-cc45dd00-b8c9-11eb-9849-1cd2df7f8603.png)
## What to do?
![image](https://user-images.githubusercontent.com/84282532/118843995-e0d6a500-b8ca-11eb-9961-2f78ca3925d1.png)


# Instalation
Only requirement to be able to install a game is camera and python>=3.6 installed.
First clone this repository using git 

``` bash
git clone https://github.com/MaxMLgh/Space_game_gesture_steering.git
```
or simply  download and unpack the ZIP file(change folder name if needed from 'Space_game_gesture_steering-master' to 'Space_game_gesture_steering' for convenience.  

![image](https://user-images.githubusercontent.com/84282532/118404730-614f9880-b674-11eb-9563-29b82fc8487e.png)


Then enter the repository:

![image](https://user-images.githubusercontent.com/73268650/118058724-248f5300-b38f-11eb-91aa-c8569f5037d3.png)

(**OPTIONAL**) Creating virtual environment. If you don't have conda skip this part.

``` bash
conda create --name Space_game python=3.8.5
conda activate Space_game
```
Installing using pip

``` bash
pip install -r requirements.txt
```
If pip can't find right version of libraries, upgrade pip and pip install again

``` bash
pip install --upgrade pip
```
To play type into command window(make sure you are in the right repository):
``` bash
python main.py
```
You can change some parameters of the game through command line arguments or simply change them in the code
``` bash
python main.py --width 1000 --height 1000 --camera 0 --folder_levels star_wars --initial_speed 10
 --speed_jump --pnt_next_lvl 100 2 --sound False --detection_confidence 0.4 --tracking_confidence 0.3
 --static_image_mode False
```
You can add folder with images to 'assets/levels/'.
Just make sure you order them correctly (1.png, 2.jpg, 3.png, ...)
![image](https://user-images.githubusercontent.com/73268650/118181763-7213ca80-b438-11eb-9aa5-5a0a2206dffa.png)  

If you want to explore MediaPipe technology of mapping:
``` bash
python main_steering.py
```
![maping_2](https://user-images.githubusercontent.com/84282532/118807654-e02d1700-b8a8-11eb-97e4-b72e7febb509.gif)


