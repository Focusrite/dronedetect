import cv2 as cv
import numpy as np
import time
from triangulate import triangulate
from color_matching import color_matching

kalman = cv.KalmanFilter(3, 3)

kalman.transitionMatrix = np.eye(3).astype('float32')
#kalman.processNoiseCov = 0.03 * np.eye(3)
#kalman.controlMatrix = 1.0 * np.eye(3)
kalman.measurementMatrix = np.eye(3).astype('float32')
initial = np.array([[0.0], [0,0], [0.0]])
i = 0
while i < 20:

    img1 = cv.imread("camera1/image_" + str(i) + ".png")
    img2 = cv.imread("camera2/cam2_" + str(i) + ".png")

    img1, det1, top_left1, bottom_right1 = color_matching(img1)
    img2, det2, top_left2, bottom_right2 = color_matching(img2)

    points1 = np.array([[[(top_left1[0] + bottom_right1[0]) / 2, (top_left1[1] + bottom_right1[1]) / 2]]])
    points2 = np.array([[[(top_left2[0] + bottom_right2[0]) / 2, (top_left2[1] + bottom_right2[1]) / 2]]])

    meas = triangulate(points1.astype('float32'), points2.astype('float32'))

    if i == 0:
        initial = meas
    prediction = kalman.predict() + initial
    correction = kalman.correct(meas - initial)
    correction = initial + correction
    i = i + 1

    cv.putText(img1, "Estimated position : " + str(int(correction[0, 0])) + " " + str(int(correction[1, 0])) + " " + str(int(correction[2, 0])), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 1.20, (255, 255, 0), 2)
    
    while True:
        cv.namedWindow('camera1', cv.WINDOW_NORMAL)
        cv.namedWindow('camera2', cv.WINDOW_NORMAL)
        cv.imshow('camera1', img1)
        cv.imshow('camera2', img2)
        ch = cv.waitKey(1)
        if ch == ord('n'):
            break

#print(ret)




#np.array([[0.5], [0.3], [0.2]]).astype('float32')
#print(meas)

#ret = kalman.correct(meas)
#print(kalman.predict())
