import numpy as np
import cv2 as cv
import os

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*9,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:9].T.reshape(-1,2)*20 # Square size = 20 mm
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

for fname in os.listdir("calibration_images"):
    if fname.endswith(".png"):
        img = cv.imread("calibration_images/" + fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (7,9), None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv.drawChessboardCorners(img, (7,9), corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(500)
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

#notice how its almost exactly the same, imagine cv2 is the namespace for cv 
#in C++, only difference is FILE_STORGE_WRITE is exposed directly in cv2
cv_file = cv.FileStorage("test.xml", cv.FILE_STORAGE_WRITE)
#creating a random matrix
print("write matrix\n", mtx)
# this corresponds to a key value pair, internally opencv takes your numpy 
# object and transforms it into a matrix just like you would do with << 
# in c++
cv_file.write("cameramatrix", mtx)
print("write dist\n", dist)
cv_file.write("distcoeffs", dist)
# note you *release* you don't close() a FileStorage object
cv_file.release()
