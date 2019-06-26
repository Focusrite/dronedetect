import cv2 as cv
import numpy as np

# Function that calculates R_1to2 and t_1to2 and saves them to r_and_t.xml
# The camera matrices and distortion coefficients have to be calculated
# and stored in camera1.xml and camera2.xml
def find_r_and_t(path1, path2):

    # Read images
    img1 = cv.imread(path1)
    img2 = cv.imread(path2)

    # array to store the object points (in 3d)
    objp = np.zeros((7*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:9].T.reshape(-1,2)*20 # Square size = 20 mm

    # Find the corners of the chess board
    found1, corners1 = cv.findChessboardCorners(img1, (7, 9), None)
    found2, corners2 = cv.findChessboardCorners(img2, (7, 9), None)

    # Read camera matrices and distortion coefficients from file
    fs1 = cv.FileStorage("camera1.xml", cv.FILE_STORAGE_READ)
    fs2 = cv.FileStorage("camera2.xml", cv.FILE_STORAGE_READ)
    c_matrix1 = fs1.getNode("cameramatrix").mat()
    c_matrix2 = fs2.getNode("cameramatrix").mat()
    dist1 = fs1.getNode("dist").mat()
    dist2 = fs2.getNode("dist").mat()
    fs1.release()
    fs2.release()

    # Undistort if needed
    #corners1 = cv.undistort(corners1, c_matrix1, dist1)
    #corners2 = cv.undistort(corners2, c_matrix2, dist2)

    # Calculate the rvecs and tvecs
    ret1, rvec1, tvec1 = cv.solvePnP(objp, corners1, c_matrix1, dist1)
    ret2, rvec2, tvec2 = cv.solvePnP(objp, corners2, c_matrix2, dist2)

    # Calculate rotation matrices from rvecs
    R1, _ = cv.Rodrigues(rvec1)
    R2, _ = cv.Rodrigues(rvec2)

    print("rvec1\n", rvec1)
    print("rvec2\n", rvec2)
    print("tvec1\n", tvec1)
    print("tvec2\n", tvec2)

    # Calculate rotation matrix and translation vector from camera 1 to 2
    R_1to2 = np.matmul(R2, np.transpose(R1))
    t_1to2 = np.matmul(R2, (-1 * np.matmul(np.transpose(R1), tvec1))) + tvec2

    # Save R and t to file
    fs = cv.FileStorage("r_and_t.xml", cv.FILE_STORAGE_WRITE)
    print("write r\n", R_1to2)
    fs.write("R", R_1to2)
    print("write t\n", t_1to2)
    fs.write("t", t_1to2)
    fs.release()    
    
if __name__ == '__main__':
    path1 = "test_camera1.png"
    path2 = "image_camera2_test.png"

    find_r_and_t(path1, path2)
