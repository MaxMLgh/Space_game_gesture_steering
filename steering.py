import cv2
import numpy as np
import math
import mediapipe as mp
mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
import time
from google.protobuf.json_format import MessageToDict


class HandDetector:
    def __init__(self, screen_height, screen_width, static_image_mode, max_hands=2,
                 detection_confidence=0.3, tracking_confidence=0.2,
                 draw_hands=True):
        self.static_image_mode = static_image_mode
        self.max_hands = max_hands
        self.draw_hands = draw_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        self.hands_detection = mp_hands.Hands(self.static_image_mode, self.max_hands,
                                              self.detection_confidence,
                                              self.tracking_confidence)

        self.tipIds = [4, 8, 12, 16, 20]
        self.img = None
        self.imgRGB = None
        self.screen_height, self.screen_width = screen_height, screen_width
        self.results = None
        self.left_hand = None
        self.right_hand = None


    def get_hands_params(self, img):
        self.img = img
        self.imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # self.left_hand = None
        # self.right_hand = None

        self.results = self.hands_detection.process(self.imgRGB)
        if not self.results.multi_hand_landmarks:
            return
        for hand_id, hand_info in enumerate(self.results.multi_hand_landmarks):
            hand_info_dict = MessageToDict(self.results.multi_handedness[hand_id])
            index = hand_info_dict['classification'][0]['index']
            prediction_confidence = hand_info_dict['classification'][0]['score']
            left_or_right = hand_info_dict['classification'][0]['label']
            point_list = []
            for id, point in enumerate(hand_info.landmark):
                point_x = int(point.x * self.screen_width)
                point_y = int(point.y * self.screen_height)
                point_z = int(point.z * self.screen_width)
                point_list.append([point_x, point_y, point_z])
            # calculate hand center
            #hand_center = center_points(point_list[0], point_list[9])
            hand_center = point_list[9][:2]

            fingers_extended = []

            thumb_index_dist = distance_points(point_list[4], point_list[10])
            index_middle_dist = distance_points(point_list[6], point_list[10])
            if thumb_index_dist > 2.5 * index_middle_dist:
                fingers_extended.append(1)
            else:
                fingers_extended.append(0)

            for id in range(1, 5):
                tip_distance = distance_points(point_list[self.tipIds[id]],
                                               point_list[self.tipIds[id]-3])
                pip_distance = distance_points(point_list[self.tipIds[id]-2],
                                               point_list[self.tipIds[id]-3])
                if tip_distance > 1.5*pip_distance:
                    fingers_extended.append(1)
                else:
                    fingers_extended.append(0)

            if self.draw_hands:
                mp_draw.draw_landmarks(img, hand_info, mp_hands.HAND_CONNECTIONS,
                                       mp_draw.DrawingSpec(color=(0, 0, 0),thickness=0,
                                           circle_radius=0),
                                       mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2,
                                           circle_radius=2)
                                       )
                # the color of the point depends on its depth
                for point in point_list:
                    color_strength = np.tanh(10 * point[2] / self.screen_width)
                    if color_strength > 0:
                        red = 0
                        green = int(color_strength * 255)
                    else:
                        red = -int(color_strength * 255)
                        green = 0
                    cv2.circle(self.img, (point[0], point[1]), 5,
                               (0, green, red), -1)
                cv2.circle(self.img, hand_center[:2], 7, (255, 0, 255),
                           cv2.FILLED)

            hand = SingleHandParameters(index, prediction_confidence, left_or_right,
                                        point_list, hand_center, fingers_extended)
            if hand.left_or_right == 'Left':
                self.left_hand = hand
            else:
                self.right_hand = hand



class SingleHandParameters:
    def __init__(self, index, prediction_confidence, left_or_right, point_dict,
                 hand_center, fingers_extended):
        self.index = index
        self.prediction_confidence = prediction_confidence
        self.left_or_right = left_or_right
        self.point_dict = point_dict
        self.hand_center = hand_center
        self.fingers_extended = fingers_extended


class Steering:
    def __init__(self,  screen_height, screen_width,  wheel_img_original='wheel_2.png',
                 arrow_img='arrow_direction.png'):
        self.wheel_img_original = cv2.imread("assets/{}".format(wheel_img_original), -1)
        self.arrow_left_img = cv2.imread("assets/{}".format(arrow_img), -1)
        self.arrow_right_img = cv2.flip(self.arrow_left_img, 1)
        self.img = None
        self.screen_height = int(screen_height)
        self.screen_width = int(screen_width)
        self.wheel_radius = None
        self.wheel_center = None
        self.wheel_angle = None
        self.turn = None
        self.shot = False
        self.shot_pause_time = time.time()

    def calculate_wheel(self, img, left_hand, right_hand):
        self.img = img
        if left_hand is None or right_hand is None:
            # self.wheel_radius = None
            # self.wheel_center = None
            # self.wheel_angle = None
            return

        wheel_radius_test = max(int(0.5 * distance_points(left_hand.hand_center[:2],
                                                          right_hand.hand_center[:2])), 10)
        if wheel_radius_test > 0.1*self.screen_width:
            wheel_radius = wheel_radius_test
        else:
            # self.wheel_radius = None
            # self.wheel_center = None
            # self.wheel_angle = None
            return

        wheel_center = center_points(left_hand.hand_center[:2], right_hand.hand_center[:2])
        #cv2.circle(self.img, wheel_center, 10, (255, 0, 255), cv2.FILLED)
        wheel_angle = math.atan2((right_hand.hand_center[1]-left_hand.hand_center[1]),
                                 (right_hand.hand_center[0]-left_hand.hand_center[0]))
        wheel_angle = -math.degrees(wheel_angle)
        self.wheel_radius = wheel_radius
        self.wheel_center = wheel_center
        self.wheel_angle = wheel_angle



    def get_commands(self, detector):
        turn = None
        shot = False
        if self.wheel_angle > 0:
            turn = min(60, (max(5, self.wheel_angle)))
        elif self.wheel_angle <= 0:
            turn = max(-60, (min(-5, self.wheel_angle)))

        fire = (detector.right_hand.fingers_extended[0] == 1 and
                detector.left_hand.fingers_extended[0] == 1 and
                not any([detector.left_hand.fingers_extended[i] for i in range(1, 5)]) and
                not any([detector.left_hand.fingers_extended[i] for i in range(1, 5)]))

        if fire:
            if time.time() - self.shot_pause_time > 0.2:
                shot = True
                self.shot_pause_time = time.time()
        self.turn = turn
        self.shot = shot
        return turn, shot



# def center_points(point_1, point_2):
#     center_x = int(0.5*(point_1[0] + point_2[0]))
#     center_y = int(0.5*(point_1[1] + point_2[1]))
#     return (center_x, center_y)
#
# def distance_points(point_1, point_2):
#     x = abs(point_1[0] - point_2[0])
#     y = abs(point_1[1] - point_2[1])
#     distance = (x**2 + y**2)**0.5
#     return distance

def center_points(point_1, point_2):
    center = [(int(0.5 * (point_1[i] + point_2[i]))) for i in range(len(point_1))]
    return center

def distance_points(point_1, point_2):
    distance = int((sum([(point_1[i] - point_2[i])**2 for i in range(len(point_1))])) ** 0.5)
    return distance

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  img_result = cv2.warpAffine(image, rot_mat, image.shape[1::-1],
                              flags=cv2.INTER_LINEAR)
  return img_result