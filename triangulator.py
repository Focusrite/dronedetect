# triangulator.py

# Defines class Triangulator that handles triangulation

import numpy as np
import cv2 as cv
import math


class Triangulator(object):
    def __init__(self):
        self.proj_matrix1 = None
        self.proj_matrix2 = None
        self.setup()

    def setup(self):
        # Get pre-calculated matrices from file
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

        # Calculate projection matrices
        self.proj_matrix1 = np.matmul(camera_matrix1, np.c_[np.eye(3), np.zeros(3)])
        self.proj_matrix2 = np.matmul(camera_matrix2, np.c_[R_1to2, t_1to2])

    # Calculates world coordinates from image coordinates
    # from_file = indicates if stored matrices should be used
    # alpha = angle between camera1 and camera2
    # beta = angle between camera1 and the angle of camera1 when
    # translation vector was known
    def triangulate(self, point1, point2, from_file=True, alpha=0.0, beta=0.0):
        if from_file:
            points_4d = cv.triangulatePoints(self.proj_matrix1, self.proj_matrix2, point1, point2)
        else:
            pmatrix1, pmatrix2 = self.estimate_pmatrices(alpha, beta)
            points_4d = cv.triangulatePoints(pmatrix1, pmatrix2, point1, point2)
            
        points_4d = points_4d / points_4d[3, 0]

        return points_4d[0:3, 0].reshape(3, 1)

    # Estimates the projection matrices
    # alpha = angle between camera1 and camera2
    # beta = angle between camera1 and the angle
    # camera1 had when t_1to2 was calculated
    # t_1to2 = translation vector at some point, currently hardcoded
    def estimate_pmatrices(self, alpha, beta):
        R = np.array([[math.cos(beta), 0, -math.sin(beta)],
                      [0, 1, 0], [math.sin(beta), 0, math.cos(beta)]])
        t_1to2 = np.array([[450.0], [1.0], [1.0]])
        t_1to2 = np.matmul(R, t_1to2)
       
        R_1to2 = np.array([[math.cos(alpha), 0, -math.sin(alpha)],
                           [0, 1, 0], [math.sin(alpha), 0, math.cos(alpha)]]).T

        # Get camera matrices
        fs1 = cv.FileStorage("camera1.xml", cv.FILE_STORAGE_READ)
        fs2 = cv.FileStorage("camera2.xml", cv.FILE_STORAGE_READ)
        c_matrix1 = fs1.getNode("cameramatrix").mat()
        c_matrix2 = fs2.getNode("cameramatrix").mat()
        fs1.release()
        fs2.release()
        # Calculate projection matrices
        pmatrix1 = np.matmul(c_matrix1, np.c_[np.eye(3), np.zeros(3)])
        pmatrix2 = np.matmul(c_matrix2, np.c_[R_1to2, t_1to2])
        
        return pmatrix1, pmatrix2

        
