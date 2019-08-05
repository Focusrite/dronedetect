import numpy as np
import cv2 as cv
import time
from pypylon import pylon
from pypylon import genicam


class Capture(object):
    def __init__(self, serial):
        self.camera = None
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.connect(serial)    

    def connect(self, serial):
        try:
            tlFactory = pylon.TlFactory.GetInstance()
            devices = tlFactory.EnumerateDevices()
            
            for device in devices:
                print(device.GetSerialNumber())
                if device.GetSerialNumber() == serial:
                    self.camera = pylon.InstantCamera(tlFactory.CreateDevice(device))
                    print("Serial: ", device.GetSerialNumber())    
            print("devices")
            #self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
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
        self.set_param('GevSCPD', 1800)
        #self.set_param('ExposureTimeAbs', 10000)
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
        else:
            print("Error. ", str(result.GetErrorCode()))
            print("\n Description: ", result.ErrorDescription)

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
    serial1 = "40016577"
    serial2 = "21810700"
    cap1 = Capture(serial1)
    cap2 = Capture(serial2)
    width1 = cap1.get_param("Width")
    height1 = cap1.get_param("Height")
    width2 = cap2.get_param("Width")
    height2 = cap2.get_param("Height")

    print("Image resolution1: " + str(width1) + ", " + str(height1))
    print("Image resolution2: " + str(width2) + ", " + str(height2))
    cap1.start()
    cap2.start()
    i = 0
    while True:
        im1 = cap1.grab()
        im2 = cap2.grab()
        if im1 is None or im2 is None:
            print("Error: Got empty result.")
            break
        cv.namedWindow('cap1', cv.WINDOW_NORMAL)
        cv.namedWindow('cap2', cv.WINDOW_NORMAL)
        cv.imshow('cap1', im1)
        cv.imshow('cap2', im2)
        ch = cv.waitKey(1)
        if ch == 27 or ch == ord('q'):
            break
        if ch == ord('s'):
            while i < 30:
                im = cap1.grab()
                cv.imwrite('calibration_images2/calib_' + str(i) + '.png', im)
                i = i + 1
                im = cap1.grab()
                time.sleep(2)
            #temp = cv.selectROI(im)
            #cv.imwrite('object.png',im)
            break

    cap1.stop()
    cap2.stop()
    cv.destroyAllWindows()
