# calculate_r_and_t.py

import cv2 as cv
import numpy as np
import math
from capture import Capture

# Function that calculates R_1to2 and t_1to2 and saves them to file_name
# The camera matrices and distortion coefficients have to be calculated
# and stored in camera1.xml and camera2.xml
def find_r_and_t(img1, img2, file_name="r_and_t.xml", cam1="camera1.xml", cam2="camera2.xml"):

    # array to store the object points (in 3d)
    objp = np.zeros((7*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:9].T.reshape(-1,2)*20 # Square size = 20 mm

    # Find the corners of the chess board
    found1, corners1 = cv.findChessboardCorners(img1, (7, 9), None)
    found2, corners2 = cv.findChessboardCorners(img2, (7, 9), None)

    # Read camera matrices and distortion coefficients from file
    fs1 = cv.FileStorage(cam1, cv.FILE_STORAGE_READ)
    fs2 = cv.FileStorage(cam2, cv.FILE_STORAGE_READ)
    c_matrix1 = fs1.getNode("cameramatrix").mat()
    c_matrix2 = fs2.getNode("cameramatrix").mat()
    dist1 = fs1.getNode("dist").mat()
    dist2 = fs2.getNode("dist").mat()
    fs1.release()
    fs2.release()

    # Calculate the rvecs and tvecs
    ret1, rvec1, tvec1, inliers = cv.solvePnPRansac(objp, corners1, c_matrix1, dist1, reprojectionError=2.0)
    ret2, rvec2, tvec2, inliers = cv.solvePnPRansac(objp, corners2, c_matrix2, dist2, reprojectionError=2.0)

    # Calculate rotation matrices from rvecs
    R1, _ = cv.Rodrigues(rvec1)
    R2, _ = cv.Rodrigues(rvec2)

    print("rvec1\n", rvec1)
    print("rvec2\n", rvec2)
    print("tvec1\n", tvec1)
    print("tvec2\n", tvec2)

    # Calculate rotation matrix and translation vector from camera 1 to 2
    R_1to2 = R2@R1.T
    t_1to2 = tvec2 -R_1to2@tvec1

    # Save R and t to file
    fs = cv.FileStorage(file_name, cv.FILE_STORAGE_WRITE)
    print("write r\n", R_1to2)
    fs.write("R", R_1to2)
    print("write t\n", t_1to2)
    fs.write("t", t_1to2)
    fs.release()
    
if __name__ == '__main__':

    # Serial numbers for the two cameras
    serial1 = "40016577"
    serial2 = "21810700"

    # Name of output file
    output_file = "r_and_t.xml"

    # Create Capture objects for the cameras
    cap1 = Capture(serial1)
    cap2 = Capture(serial2)
    cap1.start()
    cap2.start()

    img1 = cap1.grab()
    img2 = cap2.grab()

    find_r_and_t(img1, img2)

    cap1.stop()
    cap2.stop()
