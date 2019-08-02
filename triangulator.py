import numpy as np
import cv2 as cv
import math


class Triangulator(object):
    def __init__(self):
        self.proj_matrix1 = None
        self.proj_matrix2 = None
        self.setup()

    def setup(self):
        fs1 = cv.FileStorage("camera1.xml", cv.FILE_STORAGE_READ)
        fs2 = cv.FileStorage("camera2.xml", cv.FILE_STORAGE_READ)
        fs3 = cv.FileStorage("r_and_t.xml", cv.FILE_STORAGE_READ)
        camera_matrix1 = fs1.getNode("cameramatrix").mat()
        camera_matrix2 = fs2.getNode("cameramatrix").mat()
        R_1to2 = fs3.getNode("R").mat()
        t_1to2 = fs3.getNode("t").mat()
        fs1.release()
        fs2.release()
        fs3.release()

        self.proj_matrix1 = np.matmul(camera_matrix1, np.c_[np.eye(3), np.zeros(3)])
        self.proj_matrix2 = np.matmul(camera_matrix2, np.c_[R_1to2, t_1to2])

    def triangulate(self, point1, point2):
        points_4d = cv.triangulatePoints(self.proj_matrix1, self.proj_matrix2, point1, point2)
        points_4d = points_4d / points_4d[3, 0]

        return points_4d[0:3, 0].reshape(3, 1)

        
