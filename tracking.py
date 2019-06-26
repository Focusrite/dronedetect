import cv2 as cv
import numpy as np
import threading
import queue
from pypylon import pylon
from template_matching import template_matching
from boost_detection import boost_detection
from color_matching import color_matching
from cap import Capture

cap = Capture()
has_detected = False
is_detecting = False
lost_track = False
frames_tracked = 0

tracker = cv.TrackerCSRT_create()
template = cv.imread('balloon_template.png', 0)
r = 1

cap.start()

in_queue = queue.Queue()
detected_queue = queue.Queue()

def detection(in_q, out_q):
    while(True):
        if not in_q.empty():
            im, has_detected, top_left, bottom_right = color_matching(in_q.get())#, r = template_matching(in_q.get(), template, (0.2, 2.0, 10))
            out_q.put((im, has_detected, top_left, bottom_right))
            print(has_detected)
    return

t = threading.Thread(target = detection, args = (in_queue, detected_queue,))
t.setDaemon(True)
t.start()

while True:
    frame = cap.grab()
    if frame is not None:
        if not has_detected and not is_detecting:
            frames_tracked = 0
            in_queue.put(frame)
            is_detecting = True
        elif is_detecting:
            if not detected_queue.empty():
                im, has_detected, top_left, bottom_right = detected_queue.get()
                is_detecting = False
                bbox = (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
                if has_detected:
                    tracker = cv.TrackerCSRT_create()
                    ok = tracker.init(frame, bbox)
        else:
            has_detected, bbox = tracker.update(frame)
            if has_detected:
                frames_tracked = frames_tracked + 1
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv.rectangle(frame, p1, p2, (255, 0, 0), 5, 1)
                if frames_tracked > 100:
                    has_detected = False
        if frame is not None:
             cv.namedWindow('track test', cv.WINDOW_NORMAL)
             cv.imshow('track test', frame)

        ch = cv.waitKey(1)
        if ch == ord('q'):
            break    
cap.stop()        
                
        
            
                                                                            
