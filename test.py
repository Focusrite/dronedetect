import numpy as np
import cv2 as cv

from pypylon import pylon
from template_matching import template_matching

class Capture(object):
    def __init__(self):
        self.camera = None
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.connect()

    def connect(self):
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera.Open()
            print("Connecting to camera:", self.camera.GetDeviceInfo().GetModelName())
        except e:
            self.camera = None
            pass

    def start(self):
        if self.camera is None:
            print("Error: Not connected to camera, can't start grabbing.")
            return self
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        return self

    def grab(self):
        if self.camera is None or not self.camera.IsGrabbing():
            print("Error: Not connected to camera or not grabbing")
            return None
        result = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

        img = None
        if result.GrabSucceeded():
            image = self.converter.Convert(result)
            img = image.GetArray()

        result.Release()
        return img

    def stop(self):
        if self.camera is None:
            print("Error: Camera not started, can't stop.")
            return self
        self.camera.StopGrabbing()
        self.camera.Close()
        self.camera = None
        return self

    def set_param(self, param, value):
        if self.camera is None:
            print("Error: Not connected to any camera.")
            return self
        setattr(self.camera, param, value)
        return self

    def get_param(self, param):
        if self.camera is None:
            print("Error: Not connected to any camera.")
            return None
        val = getattr(self.camera, param)
        return val.GetValue()

if __name__ == '__main__':
    cap = Capture()
    width = cap.get_param("Width")
    height = cap.get_param("Height")
    print("Image resolution: " + str(width) + ", " + str(height))
    cap.start()

    template = cv.imread('magnet.png', 0)
    
    n = 0
    
    while True:
        if n == 0:
            tracker = cv.TrackerCSRT_create()
            frame = cap.grab()
            im, top_left, bottom_right  = template_matching(frame, template)
            cv.rectangle(frame, top_left, bottom_right, (255, 0, 255), 2)
            cv.imwrite('detected.png', im)
            #bbox = cv.selectROI(frame, False)
            bbox = (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
            ok = tracker.init(frame, bbox)
        else:    
            frame = cap.grab()
            if im is None:
                print("Error: Got empty result.")
                break
            timer = cv.getTickCount()
            ok, bbox = tracker.update(frame)
            #cv.rectangle(frame, top_left, bottom_right, (255, 0, 255), 2)

            fps = cv.getTickFrequency() / (cv.getTickCount() - timer)
            if ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv.rectangle(frame, p1, p2, (255, 0, 0), 5, 1)
            else:
                cv.putText(frame, "Tracking failure detected", (100,80), cv.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
            cv.namedWindow('cap', cv.WINDOW_NORMAL)
            cv.imshow('cap', frame)
            ch = cv.waitKey(1)
            if ch == ord('s'):
                cv.imwrite('test.png', im)
            if ch == ord('m'):
                    template = cv.imread('test.png', 0)
                    w, h = template.shape[::-1]
                    im_gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

                    res = cv.matchTemplate(im_gray, template, cv.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                    top_left = max_loc
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    im = cv.rectangle(im, top_left, bottom_right, (0, 0, 255), 2)
                    cv.imwrite('match.png', im)
            if ch == 27 or ch == ord('q'):
                        break
        n = n + 1
        if n == 1000:
            n = 0

    cap.stop()
    cv.destroyAllWindows()
