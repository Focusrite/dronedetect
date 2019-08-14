import numpy as np
import cv2 as cv
from template_matching import template_matching
from color_matching import color_matching
from capture import Capture

def detect(img):
    MIN_WIDTH = 28
    MIN_VALUE = 0.3
    found = False
    top_left = None
    bottom_right = None

    template = cv.imread("balloon.png", 0)
    interval = (0.8, 1.2, 5)
    
    # Blur image
    img = cv.GaussianBlur(img, (5, 5), 0)

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_red = np.array([0, 130, 120])
    upper_red = np.array([10, 255, 255])
    mask1 = cv.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 120, 120])
    upper_red = np.array([180, 255, 255])
    mask2 = cv.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2

    cnts, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL,
                              cv.CHAIN_APPROX_SIMPLE)
    cnts_sorted = sorted(cnts, key=lambda x: cv.contourArea(x), reverse = True)

    if len(cnts_sorted) > 0:
        i = 0
        while True:
            c = cnts_sorted[i]
            bbox = cv.boundingRect(c)
            cv.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 3)
            if bbox[2] < MIN_WIDTH or bbox[3] < MIN_WIDTH:
                break
            cropped = img[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]].copy()
            if cropped is None:
                print("Error: cropped is none")
            cropped, found, tl, br, max_val = template_matching(cropped, template, interval, min_value = MIN_VALUE)
            if max_val < 0.4:
                color = (0, 0, 255)
            elif max_val < 0.8:
                color = (0, 255, 255)
            else:
                color = (0, 255, 0)
            cv.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1]+bbox[3]), color, 3)
            #if found:
                #cv.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1]+bbox[3]), (0, 255, 0), 3)
                #return img, True, (bbox[0]+ tl[0], bbox[1] + tl[1]), (bbox[0] + bbox[2] + br[0], bbox[1] + bbox[3] + br[1])
            i += 1
    return img, False, top_left, bottom_right
    

if __name__ == '__main__':
    cap1 = Capture("40016577")
    cap2 = Capture("21810700")

    cap1.start()
    cap2.start()

    while True:
        timer = cv.getTickCount()
        
        frame1 = cap1.grab()
        frame2 = cap2.grab()

        if frame1 is not None and frame2 is not None:
            frame1, isfound1, tl1, br1 = detect(frame1)
            frame2, isfound2, tl2, br2 = detect(frame2)

            cv.namedWindow('camera1', cv.WINDOW_NORMAL)
            cv.imshow('camera1', frame1)
            cv.namedWindow('camera2', cv.WINDOW_NORMAL)
            cv.imshow('camera2', frame2)

        ch = cv.waitKey(1)
        if ch == 27 or ch == ord('q'):
            break
        time = cv.getTickCount() - timer
        time = time / cv.getTickFrequency()
        #print(time)
    cap1.stop()
    cap2.stop()
    cv.destroyAllWindows()
    
