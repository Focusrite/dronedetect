import numpy as np
import cv2 as cv
from pypylon import pylon

def color_matching(img):
    x, y, radius = 0, 0, 0
    #img = cv.imread('balloon.png')
    found = False

    img = cv.GaussianBlur(img, (5, 5), 0)
    
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_red = np.array([0, 130, 120])#([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 120, 120])
    upper_red = np.array([180, 255, 255])
    mask2 = cv.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2
    mask = cv.erode(mask, None, iterations=2)
    mask = cv.dilate(mask, None, iterations=2)

    cnts, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv.contourArea)
        ((x, y), radius) = cv.minEnclosingCircle(c)
        M = cv.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 50:
            found = True
            cv.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 5)
            
    return img, found, (int(x) - int(radius), int(y) - int(radius)),( int(x) + int(radius), int(y) + int(radius))   

if __name__ == '__main__':
    img = cv.imread('object.png')
    img = color_matching(img)
    
    while True:
        cv.namedWindow('orb',cv.WINDOW_NORMAL)
        cv.imshow('orb', img)
        ch = cv.waitKey(1)
        if ch == ord('q'):
            break

    cv.destroyAllWindows()    
    
