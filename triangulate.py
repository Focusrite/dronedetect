import cv2 as cv
import numpy as np
from color_matching import color_matching

# Function that calculates the real world coordinates from image points
def triangulate(point1, point2):

    # Read camera matrices, R and t
    fs1 = cv.FileStorage("camera1.xml", cv.FILE_STORAGE_READ)
    fs2 = cv.FileStorage("camera2.xml", cv.FILE_STORAGE_READ)
    fs3 = cv.FileStorage("r_and_t.xml", cv.FILE_STORAGE_READ)
    c_matrix1 = fs1.getNode("cameramatrix").mat()
    c_matrix2 = fs2.getNode("cameramatrix").mat()
    R_1to2 = fs3.getNode("R").mat()
    t_1to2 = fs3.getNode("t").mat()
    fs1.release()
    fs2.release()
    fs3.release()

    # Calculate projection matrices
    P1 = np.matmul(c_matrix1, np.c_[np.eye(3), np.zeros(3)])
    P2 = np.matmul(c_matrix2, np.c_[R_1to2, t_1to2])

    # Triangulate
    points_4d = cv.triangulatePoints(P1, P2, point1, point2)
    print(points_4d)

    # Scale the 4d coordinates
    points_4d = points_4d / points_4d[3, 0]
    print(points_4d)


if __name__ == '__main__':
    img1 = cv.imread("test_camera1.png")
    img2 = cv.imread("image_camera2_test.png")

    im1, det1, top_left1, bottom_right1 = color_matching(img1)
    im2, det2, top_left2, bottom_right2 = color_matching(img2)

    cv.namedWindow("camera1", cv.WINDOW_NORMAL)
    cv.namedWindow("camera2", cv.WINDOW_NORMAL)

    points1 = np.array([[[(top_left1[0] + bottom_right1[0]) / 2, (top_left1[1] + bottom_right1[1]) / 2]]])
    points2 = np.array([[[(top_left2[0] + bottom_right2[0]) / 2, (top_left2[1] + bottom_right2[1]) / 2]]])

    #ret, points1 = cv.findChessboardCorners(img1, (7, 9), None)
    #ret, points2 = cv.findChessboardCorners(img2, (7, 9), None)

    print(points1.astype('float32'))
    print(points2)

    triangulate(points1.astype('float32'), points2.astype('float32'))

    while True:
        cv.imshow("camera1", im1)
        cv.imshow("camera2", im2)
        ch = cv.waitKey(1)
        if ch == ord('q'):
            break
    cv.destroyAllWindows()    
