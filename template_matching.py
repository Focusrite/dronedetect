# template_matching.py

import cv2 as cv
import numpy as np

# Tries to find template in img in the scales given by interval
# using template matching
# Returns image, match, top_left, bottom_right, r where:
# image = img, with a rectangle drawn around the match if there is one
# match = true if a match was found
# top_left = top left corner of the match
# bottom_right = bottom right corner of the match
# r = indicates which scale factor the match was found for
def template_matching(img, template, interval):
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img2 = img_gray.copy() # Keep a copy of the original
    found = None
    MIN_VALUE = 0.75# minimum value needed to be a match

    w, h = template.shape[::-1]

    for scale in np.linspace(interval[0], interval[1], interval[2])[::-1]:
        img_gray = img2.copy()
        # Rescale the image
        resized = cv.resize(img_gray, (int(img_gray.shape[1]*scale), int(img_gray.shape[0]*scale)), interpolation = cv.INTER_AREA)
        r = img_gray.shape[1] / float(resized.shape[1])

        # Template must be smaller than the image!
        if resized.shape[0] < h or resized.shape[1] < w:
            break

        # Use matchTemplate and get the location of the best match
        result = cv.matchTemplate(resized, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        # If this is the best match yet, save the value, location and scale
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, r)

    if found is None:
        return img, False, (0, 0), (0, 0), 1
    
    (max_val, max_loc, r) = found
    (startX, startY) = (int(max_loc[0] * r), int(max_loc[1]* r)) # top left corner
    (endX, endY) = (int((max_loc[0] + w) * r), int((max_loc[1] + h)*r)) # bottom right corner
    cv.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)

    return img, max_val > MIN_VALUE, (startX, startY), (endX, endY), r 
   
