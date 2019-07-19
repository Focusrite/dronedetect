# https://github.com/kylehounslow/opencv-tuts/blob/master/motion-tracking-tut/final-code/motionTracking.cpp
# https://github.com/RobinDavid/Motion-detection-OpenCV/blob/master/MotionDetectorContours.py
'''
import numpy as np
import cv2 as cv

def motionDetection(thresh_img):
    object_detected = False
    temp = thresh_img.copy()
    contours, hierarchy = cv.findContours(temp, contours, hierarchy, cv.RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE)

    if contours.size() > 0:
        object_detected = True
    else:
        object_detected = False

    if object_detected is not None:
        largest_contour.append()
'''

import cv2 as cv
import numpy as np
import imutils
#import threading
#import queue
#import math
from pypylon import pylon
#from color_matching import color_matching
from cap_test import Capture
#from triangulate import triangulate
#from SimpleTracker import SimpleTracker
#from collections import OrderedDict
#from image_processing import *
#from gps import *

# Serial numbers for the two cameras
serial1 = "40016577"
serial2 = "21810700"

# Create Capture objects for the cameras
cap1 = Capture(serial1)
cap2 = Capture(serial2)

# Start cameras
cap1.start()
cap2.start()

firstFrame1 = None
firstFrame2 = None

while True:
    timer = cv.getTickCount()
    
    points1 = None
    points2 = None
    
    # Grab image from cameras
    frame1 = cap1.grab()
    frame2 = cap2.grab()

    if frame1 is not None and frame2 is not None:
        # resize the frame, convert it to grayscale, and blur it
        frame1 = imutils.resize(frame1, width=500)
        frame2 = imutils.resize(frame2, width=500)
        gray1 = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
        gray1 = cv.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
        gray2 = cv.GaussianBlur(gray2, (21, 21), 0)
 
    if frame1 is None and frame2 is None:
        print("Error. empty frame\n")
        break

    if firstFrame1 is None and firstFrame2 is None:
        firstFrame1 = gray1
        firstFrame2 = gray2
        continue

    frameDiff = cv.absdiff(firstFrame1, gray1)
    thresh1 = cv.threshold(frameDiff, 25, 255, cv.THRESH_BINARY)[1]

    thresh1 = cv.dilate(thresh1, None, iterations=2)
    cnts = cv.findContours(thresh1.copy(), cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        if cv.contourArea(c) < 30:
            continue
        (x,y,w,h) = cv.boundingRect(c)
        cv.rectangle(frame1, (x,y),(x+w,y+h),(0,255,0),2)

    if frame1 is not None:
        cv.namedWindow('camera1', cv.WINDOW_NORMAL)
        cv.imshow('camera1', frame1)
        cv.namedWindow('thresh1', cv.WINDOW_NORMAL)
        cv.imshow('thresh1', thresh1)
    
    if frame2 is not None:
        cv.namedWindow('camera2', cv.WINDOW_NORMAL)
        time = cv.getTickCount() - timer
        cv.putText(frame2, "time: " + str(time / cv.getTickFrequency()), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
        cv.imshow('camera2', frame2)

    ch = cv.waitKey(1)
    if ch == ord('q'):
        break

cap1.stop()
cap2.stop()
cv.destroyAllWindows()

                
        
            
                                                                            
