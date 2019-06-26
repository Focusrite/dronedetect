# template_matching.py

import cv2 as cv
import numpy as np
import sys
from pypylon import pylon
#from skimage.util import random_noise

def template_matching(img,template, interval):
    #img = cv.resize(img, (int(img.shape[1]*0.5), int(img.shape[0] * 0.5)), interpolation = cv.INTER_AREA)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img2 = img_gray.copy()
    found = None

    w, h = template.shape[::-1]

    for scale in np.linspace(interval[0], interval[1], interval[2])[::-1]:
        img_gray = img2.copy()
        resized = cv.resize(img_gray, (int(img_gray.shape[1]*scale), int(img_gray.shape[0]*scale)), interpolation = cv.INTER_AREA)
        r = img_gray.shape[1] / float(resized.shape[1])

        if resized.shape[0] < h or resized.shape[1] < w:
            break

        edged = resized#cv.Canny(resized, 50, 200)
        result = cv.matchTemplate(edged, template, cv.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        if found is None or max_val > found[0]:
            found = (max_val, max_loc, r)

    (max_val, max_loc, r) = found
    (startX, startY) = (int(max_loc[0] * r), int(max_loc[1]* r))
    (endX, endY) = (int((max_loc[0] + w) * r), int((max_loc[1] + h)*r))
    cv.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)

    print("max_val is ", max_val)
    return img, max_val > 0.7, (startX, startY), (endX, endY), r 

def test():

    img = cv.imread('images/findballoon_red.png')
    img = cv.GaussianBlur(img, (10,10),0)
    
    #salt-and-pepper noise
    #img = random_noise(img, mode='s&p',amount=0.3)
    #img = np.array(255*img, dtype='uint8')
    #img = cv.medianBlur(img,5)

    template = cv.imread('images/ballong.png', 0)
    template = cv.Canny(template, 50, 200)
    img = template_matching(img, template)

    while True:
        cv.namedWindow('test', cv.WINDOW_NORMAL)
        cv.imshow('test', img)
        ch = cv.waitKey(1)
        if ch == ord('q'):
            break
    cv.destroyAllWindows() 

if __name__ =='__main__':
   test()
