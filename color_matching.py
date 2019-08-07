# color_matching.py

import numpy as np
import cv2 as cv
from pypylon import pylon

# Function that tries to find red areas in an image img
# Returns img, found, top_left, bottom_right where:
# img = the image, with a rectangle drawn around the found area
# found = true if a red area has been found
# top_left, bottom_right = the top left and bottom right corners
# of the found area
def color_matching(img):
    # Initialize default values
    x, y, radius = 0, 0, 0
    found = False
    MIN_RADIUS = 8

    # Blur image
    img = cv.GaussianBlur(img, (5, 5), 0)

    # Change image to HSV colour space
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Mask out the lower interval
    lower_red = np.array([0, 130, 120])
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
        # Find the bounding rectangle
        bbox = cv.boundingRect(c)

        if radius > MIN_RADIUS:
            found = True
            cv.rectangle(img, (bbox[0], bbox[0] + bbox[2]), (bbox[1], bbox[1] + bbox[3]), (0, 255, 0), 3)
    return img, found, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])        
    #return img, found, (int(x) - int(radius), int(y) - int(radius)),( int(x) + int(radius), int(y) + int(radius))   

   
    
