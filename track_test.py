import cv2 as cv
import numpy as np
import threading
from pypylon import pylon
from template_matching import template_matching
from cap import Capture
from color_matching import color_matching

cap = Capture()
has_detected = False
lost_track = False
frames_tracked = 0
tracker = cv.TrackerCSRT_create()
template = cv.imread('magnet.png', 0)
r = 1
time = 0

cap.start()

while True:
    frame = cap.grab()
    if not (has_detected):
        if frame is None:
            print("Error. empty result")
        else:
            timer = cv.getTickCount()
            #im, has_detected, top_left, bottom_right = color_matching(frame)
            im, has_detected, top_left, bottom_right, r = template_matching(frame, template, (0.2, 2.0, 10))
            if has_detected:
                time = cv.getTickCount() - timer
                bbox = (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
                tracker = cv.TrackerCSRT_create()
                ok = tracker.init(frame, bbox)
            frames_tracked = 0
    elif lost_track:
        if frame is not None:
            timer = cv.getTickCount()
            im, has_detected, top_left, bottom_right, r = template_matching(frame, template, (1 / r - 0.2 , 1/r + 0.2, 5))
            #im, has_detected, top_left, bottom_right = color_matching(frame)
            time = cv.getTickCount() - timer
            bbox = (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
            tracker = cv.TrackerCSRT_create()
            ok = tracker.init(frame, bbox)
            #cv.putText(frame, "time to detect: " + str(time), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
            frames_tracked = 0
            if has_detected:
                lost_track = False
    else:
        if frame is None:
            print("Error. Empty result")
        else:    
            timer = cv.getTickCount()
            ok, bbox = tracker.update(frame)

            fps = cv.getTickFrequency() / (cv.getTickCount() - timer)
            if ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv.rectangle(frame, p1, p2, (255, 0, 0), 5, 1)
                cv.putText(frame, "fps: " + str(fps), (100, 80), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
                frames_tracked = frames_tracked + 1
            else:
                lost_track = True
                cv.putText(frame, "Tracking failure detected", (100, 80), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
    if frame is not None:
        cv.putText(frame, "time to detect: " + str(time / cv.getTickFrequency()), (100, 200), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
        cv.namedWindow('track test', cv.WINDOW_NORMAL)
        cv.imshow('track test', frame)

    ch = cv.waitKey(1)
    if ch == ord('q'):
        break

cap.stop()
