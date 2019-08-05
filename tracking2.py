import cv2 as cv
import numpy as np
import threading
import queue
from pypylon import pylon
from color_matching import color_matching
from capture import Capture
from triangulate import triangulate

# Serial numbers for the two cameras
serial1 = "40016577"
serial2 = "21810700"

# Create Capture objects for the cameras
cap1 = Capture(serial1)
cap2 = Capture(serial2)

# Start cameras
cap1.start()
cap2.start()

kalman = cv.KalmanFilter(3, 3)
kalman.transitionMatrix = np.eye(3).astype('float32')
kalman.measurementMatrix = np.eye(3).astype('float32')
kalman.measurementNoiseCov = np.array([[7.13, 0.0, 0.0], [0.0, 11.02, 0.0], [0.0, 0.0, 100.62]]).astype('float32')
initiated = False
initial = np.array([[0.0], [0.0], [0.0]])

while True:
    # Grab image from cameras
    frame1 = cap1.grab()
    frame2 = cap2.grab()

    if frame1 is not None and frame2 is not None:
        # Detect the balloon
        im, has_detected, top_left1, bottom_right1 = color_matching(frame1)
        im, has_detected2, top_left2, bottom_right2 = color_matching(frame2)
    else:
        print("Error. empty frame\n")
        break

    if has_detected and has_detected2:
        # Find the center of the balloon
        points1 = np.array([[[(top_left1[0] + bottom_right1[0]) / 2, (top_left1[1] + bottom_right1[1]) / 2]]])
        points2 = np.array([[[(top_left2[0] + bottom_right2[0]) / 2, (top_left2[1] + bottom_right2[1]) / 2]]])
        
        # Estimate balloon position
        pos = triangulate(points1.astype('float32'), points2.astype('float32'))

        if not initiated:
            initial = pos
            initiated = True

        pred = kalman.predict() + initial
        corr = kalman.correct(pos - initial) + initial
            
        
        cv.putText(frame1, "Estimated position : " + str(int(corr[0, 0])) + " " + str(int(corr[1, 0])) + " " + str(int(corr[2, 0])), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 1.75, (255, 255, 0), 3)

    cv.rectangle(frame1, top_left1, bottom_right1, (255, 0, 0), 3)
    cv.rectangle(frame2, top_left2, bottom_right2, (255, 0, 0), 3)


    if frame1 is not None:
        cv.namedWindow('camera1', cv.WINDOW_NORMAL)
        cv.imshow('camera1', frame1)
    if frame2 is not None:
        cv.namedWindow('camera2', cv.WINDOW_NORMAL)
        cv.imshow('camera2', frame2)

    ch = cv.waitKey(1)
    if ch == ord('q'):
        break

cap1.stop()
cap2.stop()
cv.destroyAllWindows()
                
        
            
                                                                            
