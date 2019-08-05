"""calibrate_camera.py

Calibrates a camera using chessboard images. If there are multiple cameras connected, only the first to be found will be calibrated.

The resulting camera matrix and distortion coefficients are stored in the output file.

Usage:
    calibrate_camera.py [--output=<file>] [--sqsize=<mm>]
    calibrate_camera.py [--output=<file>] [--sqsize=<mm>] --bwidth=<sqs> --bheight=<sqs>

Options:
    --help, -h                    Print this help message.
    --output=<file>, -o <file>    [Default: camera_test.xml] The output file to send the camera parameters to.
    --sqsize=<mm>, -s <mm>        [Default: 20] The chessboard square size in mm.
    --bwidth=<sqs>, -bw <sqs>     [Default: 7] The chessboard width in squares.
    --bheight=<sqs>, -bh <sqs>    [Default: 9] The chessboard height in squares.

"""


import numpy as np
import cv2 as cv
import docopt
from cap import Capture

def calibrate(output_file, square_size, board_width, board_height):
    print("CALIBRATING CAMERA")
    
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ... (6,8,0)
    objp = np.zeros((board_width * board_height, 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_width, 0:board_height].T.reshape(-1,2)*float(square_size)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d points in real world space
    imgpoints = [] # 2d points in image plane

    cap = Capture()
    cap.start()

    good_images = 0
    while good_images < 25:
        print("Grabbing picture")
        img = cap.grab()
        print("Picture grabbed")
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (board_width,board_height), None)
        print("Found chessboard corners")

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            # Draw and display the corners
            cv.drawChessboardCorners(img, (board_width, board_height), corners2, ret)
            cv.namedWindow('img', cv.WINDOW_NORMAL)
            cv.imshow('img', img)
            cv.waitKey(500)
            good_images += 1
        else:
            print("Could not find corners")
    cv.destroyAllWindows()
    cap.stop()

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    cv_file = cv.FileStorage(output_file, cv.FILE_STORAGE_WRITE)
    cv_file.write("cameramatrix", mtx)
    cv_file.write("distcoeffs", dist)
    cv_file.release()

if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    output_file = args["--output"]

    square_size = args["--sqsize"]
    board_width = args["--bwidth"]
    board_height = args["--bheight"]
    calibrate(output_file, square_size, int(board_width), int(board_height))
