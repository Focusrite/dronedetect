import cv2 as cv
import numpy as np
from pypylon import pylon
from template_matching import template_matching
from cap import Capture

cap = Capture()
has_detected = False
frames_tracked = 0
tracker = None
template = cv.imread('magnet.png', 0)

cap.start()

while True:
    if not (has_detected):
        frame = cap.grab()
        if frame is None:
            print("Error. empty result")
        else:    
            im, has_detected, top_left, bottom_right = template_matching(frame, template)
            bbox = (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
            tracker = cv.TrackerCSRT_create()
            ok = tracker.init(frame, bbox)
            frames_tracked = 0
    else:
        frame = cap.grab()
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
                has_detected = False
                cv.putText(frame, "Tracking failure detected", (100, 80), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
    if frame is not None:            
        cv.namedWindow('track test', cv.WINDOW_NORMAL)
        cv.imshow('track test', frame)

    ch = cv.waitKey(1)
    if ch == ord('q'):
        break

cap.start()
img = cap.grab()
cv.imwrite('snapshot.png', img)
cap.stop()
