# detector.py

import numpy as np
import cv2 as cv

class Detector(object):
    def __init__(self):
        self.MIN_WIDTH = 30
        self.MIN_VALUE = 0.75
        self.MAX_VALUE = 0.15

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

    def color_detection(self, img):
        found = False
        bbox = [0, 0, 0, 0]
        cnts = self.get_red_contours(img)
        if len(cnts) > 0:
            c = max(cnts, key = cv.contourArea)
            bbox = cv.boundingRect(c)

            if bbox[2] >= self.MIN_WIDTH and bbox[3] >= self.MIN_WIDTH:
                found = True
        return img, found, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])

    def get_red_contours(self, img):
        img = cv.GaussianBlur(img, (5, 5), 0)
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        
        lower_red = np.array([0, 120, 120])
        upper_red = np.array([10, 255, 255])
        mask1 = cv.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 120, 120])
        upper_red = np.array([180, 255, 255])
        mask2 = cv.inRange(hsv, lower_red, upper_red)

        mask = mask1 + mask2
        cnts, _ = cv.findContours(mask.copy(), cv.RETR_EXTERNAL,
                                  cv.CHAIN_APPROX_SIMPLE)
        return cnts

    def detection(self, img):
        cnts = self.get_red_contours(img)
        cnts_sorted = sorted(cnts, key=lambda x: cv.contourArea(x), reverse = True)
        if len(cnts) > 0:
            i = 0
            while True:
                c = cnts_sorted[i]
                bbox = cv.boundingRect(c)
                if bbox[2] < self.MIN_WIDTH or bbox[3] < self.MIN_WIDTH:
                    return img, False, [0, 0], [0, 0]
                    break
                match = cv.matchShapes(self.template, c, 1, 0.0)
                if match < self.MAX_VALUE:
                    return img, True, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3])
                i += 1
        return img, False, [0, 0], [0, 0]

    def template_detection(self, img, template):
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img2 = img_gray.copy()
        found = None

        w, h = template.shape[::-1]

        for scale in np.linspace(interval[0], interval[1], interval[2])[::-1]:
            img_gray = img2.copy()
            resized = cv.resize(img_gray, (int(img_gray.shape[1]*scale), int(img_gray.shape[0]*scale)), interpolation = cv.INTER_AREA)
            r = img_gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < h or resized.shape[1] < w:
                continue # break?

            result = cv.matchTemplate(resized, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

            if found is None or max_val > found[0]:
                found = (max_val, max_loc, r)

        (max_val, max_loc, r) = found
        (startX, startY) = (int(max_loc[0] * r), int(max_loc[1] * r))
        (endX, endY) = (int((max_loc[0] + w) * r), int((max_loc[1] + h) * r))

        return img, max_val > self.MIN_VALUE, (startX, startY), (endX, endY)
        
