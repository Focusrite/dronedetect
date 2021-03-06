# image_processing.py
# Main program for the image processing module

import cv2 as cv
import numpy as np
import math
from pypylon import pylon
from capture import Capture
from SimpleTracker import SimpleTracker
from collections import OrderedDict
from TCPClient import *
from gps import *
import globals
from triangulator import Triangulator
from detector import Detector

def tracking():
    # Initiera globala variabler
    globals.initialize()

    # Create Triangulator object
    triangulator = Triangulator()

    # Create Detector object
    detector = Detector()
    
    # Serial numbers for the two cameras
    serial1 = "40016577"
    serial2 = "21810700"

    # Create Capture objects for the cameras
    cap1 = Capture(serial1)
    cap2 = Capture(serial2)

    # Start cameras
    cap1.start()
    cap2.start()

    # Kalman filter
    kalman = cv.KalmanFilter(3, 3)
    kalman.transitionMatrix = np.eye(3).astype('float32')
    kalman.measurementMatrix = np.eye(3).astype('float32')
    kalman.measurementNoiseCov = np.array([[7.13, 0.0, 0.0], [0.0, 11.02, 0.0], [0.0, 0.0, 100.62]]).astype('float32')
    initiated = False
    initial = np.array([[0.0], [0.0], [0.0]])

    # Trackers
    tracker1 = SimpleTracker()
    tracker2 = SimpleTracker()

    #Set up connection to server
    sock = connect_to_server('192.168.1.130')
    send_message(sock, 0, 'N', 0, 0, 0)
    listening_thread = threading.Thread(target = read_message, args=(sock,), daemon = True)
    listening_thread.start()

    # Angle that indicates the direction that camera1 points
    # NORTH = 0, WEST = pi/2, SOUTH = pi, EAST = -pi/2
    angle = 0

    times_found = 0

    while True:
        if globals.image_processing_abort:
            break

        if globals.image_processing_begin:
            timer = cv.getTickCount()
    
            points1 = None
            points2 = None
    
            # Grab image from cameras
            frame1 = cap1.grab()
            frame2 = cap2.grab()

            if frame1 is not None and frame2 is not None:
                # Detect the balloon
                im, has_detected, top_left1, bottom_right1 = detector.detection(frame1)        
                im, has_detected2, top_left2, bottom_right2 = detector.detection(frame2)

                # Update trackers
                if has_detected:
                    objects1 = tracker1.update([(top_left1[0], top_left1[1], bottom_right1[0], bottom_right1[1])])
                else:
                    objects1 = tracker1.update([])
                if has_detected2:
                    objects2 = tracker2.update([(top_left2[0], top_left2[1], bottom_right2[0], bottom_right2[1])])
                else:
                    objects2 = tracker2.update([])
            else:
                print("Error. empty frame\n")
                break

            # Find the center of the balloon
            if bool(objects1):
                obj = list(objects1.items())
                points1 = np.array([[[obj[0][1][0], obj[0][1][1]]]])
            if bool(objects2):
                obj = list(objects2.items())
                points2 = np.array([[[obj[0][1][0], obj[0][1][1]]]])

            if points1 is not None and points2 is not None:
                
                # Estimate balloon position relative to camera
                pos = triangulator.triangulate(points1.astype('float32'), points2.astype('float32'))

                if pos[2, 0] > 0: # Estimated position must be in front of camera
                    times_found += 1
                    
                    # Start the kalman filter if this was the first measurement
                    if not initiated:
                        initial = pos.astype('float32')
                        initiated = True

                    # Update kalman filter
                    pred = kalman.predict() + initial
                    corr_pos = kalman.correct(pos - initial) + initial
            
                    # Convert to EDN coordinates
                    corr_pos = edn_from_camera(corr_pos, angle).astype('float64')

                    # Convert to gps position
                    # We must multiply pos with 0.001 since pos is in mm and gps_from_edn expects m
                    gps_pos = gps_from_edn(np.array([[globals.latitude], [globals.longitude], [globals.altitude]]).astype('float64'), corr_pos * 0.001)

                    if globals.image_processing_send and times_found > 10:
                        send_message(sock, 1, 'M', gps_pos[1, 0], gps_pos[0, 0], gps_pos[2, 0])
                        globals.image_processing_send = False
        
                    cv.putText(frame1, "Estimated position : " + str(int(corr_pos[0, 0])) + " " + str(int(corr_pos[1, 0])) + " " + str(int(corr_pos[2, 0])), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 1.75, (255, 255, 0), 3)

            # Draw rectangles around the found balloons
            if has_detected:
                cv.rectangle(frame1, top_left1, bottom_right1, (255, 0, 0), 3)

            if has_detected2:    
                cv.rectangle(frame2, top_left2, bottom_right2, (255, 0, 0), 3)


            # Show frames in windows
            if frame1 is not None:
                cv.namedWindow('camera1', cv.WINDOW_NORMAL)
                cv.imshow('camera1', frame1)
            if frame2 is not None:
                cv.namedWindow('camera2', cv.WINDOW_NORMAL)
                time = cv.getTickCount() - timer
                cv.putText(frame2, "time: " + str(time / cv.getTickFrequency()), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
                cv.imshow('camera2', frame2)
    
            ch = cv.waitKey(1)
            if ch == 27 or ch == ord('q'):
                break

    cap1.stop()
    cap2.stop()
    cv.destroyAllWindows()

tracking()    
                
        
            
                                                                            
