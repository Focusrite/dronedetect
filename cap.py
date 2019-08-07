# cap.py

# Defines the Capture class used to access a camera
# Always accesses the first camera found

import numpy as np
import cv2 as cv
import time
from pypylon import pylon
from pypylon import genicam


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
        except genicam.GenericException as e:
            self.camera = None
            pass

    def start(self):
        if self.camera is None:
            print("Error: Not connected to camera, can't start grabbing.")
            return self
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        self.set_param('GainAuto', 'Continuous')
        self.set_param('AcquisitionFrameRateEnable', True)
        self.set_param('AcquisitionFrameRateAbs', 20.0)
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
    i = 0
    while True:
        im = cap.grab()
        if im is None:
            print("Error: Got empty result.")
            break
        cv.namedWindow('cap', cv.WINDOW_NORMAL)
        cv.imshow('cap', im)
        ch = cv.waitKey(1)
        if ch == 27 or ch == ord('q'):
            break
        if ch == ord('s'):
            temp = cv.selectROI(im)
            cv.imwrite('object.png',im)
            break

    cap.stop()
    cv.destroyAllWindows()
