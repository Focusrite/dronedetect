import cv2 as cv
import numpy as np
from pypylon import pylon

img = cv.imread('balloon.png')
img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img2 = img_gray.copy()

found = None

template = cv.imread('ballong.png', 0)

w, h = template.shape[::-1]

for scale in np.linspace(0.2, 1.0, 10)[::-1]:
    img_gray = img2.copy()
    resized = cv.resize(img_gray, (int(img_gray.shape[1]*scale), int(img_gray.shape[0]*scale)), interpolation = cv.INTER_AREA)
    r = img_gray.shape[1] / float(resized.shape[1])

    if resized.shape[0] < h or resized.shape[1] < w:
        break

    edged = cv.Canny(resized, 50, 200)
    result = cv.matchTemplate(edged, template, cv.TM_CCOEFF)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    if found is None or max_val > found[0]:
        found = (max_val, max_loc, r)

(_, max_loc, r) = found
(startX, startY) = (int(max_loc[0] * r), int(max_loc[1]* r))
(endX, endY) = (int((max_loc[0] + w) * r), int((max_loc[1] + h)*r))

cv.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)

while True:
    cv.namedWindow('test', cv.WINDOW_NORMAL)
    cv.imshow('test', img)
    ch = cv.waitKey(1)
    if ch == ord('q'):
        break
cv.destroyAllWindows()    
