import cv2 as cv
import numpy as np
#from SimpleTracker import SimpleTracker


def track():

    # Load the classifier with the trained weights
    drone_cascade = cv.CascadeClassifier('/home/user/sommarjobb/drone_classifier/classifier/cascade.xml')

    # Load video
    cap = cv.VideoCapture('/home/user/sommarjobb/drone_classifier/drone_video.mp4')

    # Use tracker algorithm
    #tracker = SimpleTracker()

    while True:

        # Read from video frame by frame
        ret, img = cap.read() 
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Detect the drone
        drones = drone_cascade.detectMultiScale(gray, 1.3, 5)
            
        # Draw rectangle around detected drone
        for (x,y,w,h) in drones:
            cv.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
            font = cv.FONT_HERSHEY_SIMPLEX
            cv.putText(img, 'Drone', (x-w, y-h), font, 0.5, (0,255,255), 2, cv.LINE_AA)

        # Update trackers
        #if drones is not None:
        #    objects = tracker.update([(x,y,x+w,y+h)])
        #else:
        #    objects = tracker.update([])

        # Show frame
        cv.imshow('img',img)
        
        # Wait for key to show next frame
        k = cv.waitKey(0)

        # Quit if q or esc is pressed
        if k == 27 or k ==ord('q'):
            break

    cap.release()

    cv.destroyAllWindows()

track()
