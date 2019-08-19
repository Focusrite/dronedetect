# detector.py
# Defines class Detector used for detection of balloon

import numpy as np
import cv2 as cv

class Detector(object):
    def __init__(self):
        self.MIN_WIDTH = 30 # min width of a red area
        self.MIN_VALUE = 0.75 # min value needed for template match
        self.MAX_VALUE = 0.15 # max value for shape match

        # Load the template and extract contour
        temp = cv.imread("template.png")
        temp = cv.cvtColor(temp, cv.COLOR_BGR2HSV)
        mask1 = cv.inRange(temp, np.array([0, 130, 70]),
                           np.array([8, 255, 255]))
        mask2 = cv.inRange(temp, np.array([172, 130, 70]),
                           np.array([180, 255, 255]))
        mask = mask1 + mask2
        cnts, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        self.template = max(cnts, key=cv.contourArea)
        if self.template is None:
            print("Error: no template found")

    # Tries to detect balloon by finding largest red area
    def color_detection(self, img):
        found = False
        bbox = [0, 0, 0, 0]
        # Find contours around red areas
        cnts = self.get_red_contours(img)
        if len(cnts) > 0:
            c = max(cnts, key = cv.contourArea) # find largest contour
            bbox = cv.boundingRect(c) # find bounding rectangle

            if bbox[2] >= self.MIN_WIDTH and bbox[3] >= self.MIN_WIDTH:
                found = True # if large enough, it's a match
        return img, found, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])

    # Get all contours around red areas
    def get_red_contours(self, img):
        img = cv.GaussianBlur(img, (5, 5), 0) # Blur image
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV) # convert to HSV

        # Mask out lower red interval
        lower_red = np.array([0, 120, 120])
        upper_red = np.array([10, 255, 255])
        mask1 = cv.inRange(hsv, lower_red, upper_red)

        # Mask out upper red interval
        lower_red = np.array([170, 120, 120])
        upper_red = np.array([180, 255, 255])
        mask2 = cv.inRange(hsv, lower_red, upper_red)

        mask = mask1 + mask2 # add masks

        # Find contours
        cnts, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL,
                                  cv.CHAIN_APPROX_SIMPLE)
        return cnts

    # Function that tries to detect red balloon
    def detection(self, img):
        cnts = self.get_red_contours(img) # find contours
        # sort contours by contour area
        cnts_sorted = sorted(cnts, key=lambda x: cv.contourArea(x), reverse = True)
        i = 0
        while len(cnts) > i:
            c = cnts_sorted[i]
            bbox = cv.boundingRect(c) # find bounding rectangle
            if bbox[2] < self.MIN_WIDTH or bbox[3] < self.MIN_WIDTH:
                # if the rectangle is too small, return
                return img, False, [0, 0], [0, 0]
            match = cv.matchShapes(self.template, c, 1, 0.0) # match with template contour
            if match < self.MAX_VALUE:
                # if match is close enough, it's a detection
                return img, True, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])
            i += 1
        return img, False, [0, 0], [0, 0]

    # Function that tries to detect red balloon using template matching
    # template should be in gray scale
    def template_detection(self, img, template):
        interval = (0.8, 1.2, 5)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img2 = img_gray.copy() # keep a copy of the original
        found = None

        w, h = template.shape[::-1] # get size of template image

        for scale in np.linspace(interval[0], interval[1], interval[2])[::-1]:
            img_gray = img2.copy()
            # Resize the image
            resized = cv.resize(img_gray, (int(img_gray.shape[1]*scale), int(img_gray.shape[0]*scale)), interpolation = cv.INTER_AREA)
            r = img_gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < h or resized.shape[1] < w: # image must not be smaller than template
                continue

            result = cv.matchTemplate(resized, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

            if found is None or max_val > found[0]:
                found = (max_val, max_loc, r)

        (max_val, max_loc, r) = found
        (startX, startY) = (int(max_loc[0] * r), int(max_loc[1] * r))
        (endX, endY) = (int((max_loc[0] + w) * r), int((max_loc[1] + h) * r))

        return img, max_val > self.MIN_VALUE, (startX, startY), (endX, endY)
        
