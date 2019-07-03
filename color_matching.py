import numpy as np
import cv2 as cv
from pypylon import pylon

def color_matching(img):
    # Initialize default values
    x, y, radius = 0, 0, 0
    found = False

    # Blur image
    img = cv.GaussianBlur(img, (5, 5), 0)

    # Change image to HSV colour space
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Mask out the lower interva
    lower_red = np.array([0, 130, 120])#([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv.inRange(hsv, lower_red, upper_red)

    # Mask out the upper interval
    lower_red = np.array([170, 120, 120])
    upper_red = np.array([180, 255, 255])
    mask2 = cv.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2
    #mask = cv.erode(mask, None, iterations=2)
    #mask = cv.dilate(mask, None, iterations=2)

    # Find contours
    cnts, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:
        # Pick the largest contour
        c = max(cnts, key=cv.contourArea)

        # Find the smallest enclosing circle
        ((x, y), radius) = cv.minEnclosingCircle(c)
        bbox = cv.boundingRect(c)
        #M = cv.moments(c)
        #center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 50:
            found = True
            cv.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 3)
            cv.rectangle(img, (bbox[0], bbox[0] + bbox[2]), (bbox[1], bbox[1] + bbox[3]), (0, 255, 0), 3)
            #cv.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 5)
            #print(bbox[0], bbox[1], bbox[2], bbox[3])
    #return img, found, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])        
    return img, found, (int(x) - int(radius), int(y) - int(radius)),( int(x) + int(radius), int(y) + int(radius))   

if __name__ == '__main__':
    img = cv.imread('object.png')
    img = color_matching(img)
    
    while True:
        cv.namedWindow('orb',cv.WINDOW_NORMAL)
        cv.imshow('orb', img[0])
        ch = cv.waitKey(1)
        if ch == ord('q'):
            break

    cv.destroyAllWindows()    
    
