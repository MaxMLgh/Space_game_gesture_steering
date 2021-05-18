import cv2
import time
import argparse
from steering import HandDetector, SingleHandParameters, Steering
from steering import center_points, distance_points, rotate_image

def main():
    vid = cv2.VideoCapture(0)
    scale = 0.5
    screen_height = scale * vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    screen_width = scale * vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    detector = HandDetector(screen_height, screen_width, static_image_mode=False, draw_hands=True)

    while True:
        start_time = time.time()
        _, img = vid.read()
        img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
        img = cv2.flip(img, 1)
        detector.get_hands_params(img)

        FPS = round(1/(time.time() - start_time), 1)
        cv2.putText(img, 'FPS:{}'.format(FPS), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

        if cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            vid.release()
            cv2.destroyAllWindows()



if __name__ == "__main__":
    main()