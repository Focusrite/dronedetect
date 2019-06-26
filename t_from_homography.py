import cv2 as cv
import numpy as np

def find_r_and_t(path1, path2):
    img1 = cv.imread(path1)
    img2 = cv.imread(path2)

    objp = np.zeros((7*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:9].T.reshape(-1,2)*20 # Square size = 20 mm

    found1, corners1 = cv.findChessboardCorners(img1, (7, 9), None)
    found2, corners2 = cv.findChessboardCorners(img2, (7, 9), None)

    fs1 = cv.FileStorage("camera1.xml", cv.FILE_STORAGE_READ)
    fs2 = cv.FileStorage("camera2.xml", cv.FILE_STORAGE_READ)

    c_matrix1 = fs1.getNode("cameramatrix").mat()
    c_matrix2 = fs2.getNode("cameramatrix").mat()
    dist1 = fs1.getNode("dist").mat()
    dist2 = fs2.getNode("dist").mat()
    fs1.release()
    fs2.release()

    #corners1 = cv.undistort(corners1, c_matrix1, dist1)
    #corners2 = cv.undistort(corners2, c_matrix2, dist2)

    ret1, rvec1, tvec1 = cv.solvePnP(objp, corners1, c_matrix1, dist1)
    ret2, rvec2, tvec2 = cv.solvePnP(objp, corners2, c_matrix2, dist2)

    print("rvec1\n", rvec1)
    print("rvec2\n", rvec2)
    print("tvec1\n", tvec1)
    print("tvec2\n", tvec2)
    
    R_1to2 = np.matmul(rvec2, np.transpose(rvec1))
    t_1to2 = rvec2 * (-1 * np.matmul(np.transpose(rvec1), tvec1)) + tvec2
    
    fs = cv.FileStorage("r_and_t.xml", cv.FILE_STORAGE_WRITE)
    print("write r\n", R_1to2)
    fs.write("R", R_1to2)
    print("write t\n", t_1to2)
    fs.write("t", t_1to2)
    fs.release()    

def triangulate(corners1, corners2):
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
    P1 = np.matmul(c_matrix1, np.c_[np.eye(3), np.zeros(3)])
    P2 = np.matmul(c_matrix2, np.c_[R_1to2, t_1to2])
    print(corners1[0, 0])
    points_4d = cv.triangulatePoints(P1, P2, corners1[0, 0], corners2[0, 0])
    r, k = points_4d.shape
    print(r, k)
    print(points_4d)
    points_4d = points_4d / points_4d[3, 0]
    print(points_4d)
    
if __name__ == '__main__':
    path1 = "chessboard1.png"
    path2 = "chessboard2.png"

    find_r_and_t(path1, path2)
