import cv2 as cv
import numpy as np
from pypylon import pylon

def boost_detection(img, trained_model):
    boost = cv.ml.Boost_create()
    boost = boost.load(trained_model)

    win_size = (600, 400)
    cell_size = (50, 50)
    block_size = (100, 100)
    block_stride = (50, 50)
    nbins = 9
    hog = cv.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins, 1, -1, 0, 0.2, 1, 64, False)

    h, w, _ = img.shape

    im = cv.resize(img, (600, 400), cv.INTER_AREA)
    
    descriptor = hog.compute(im)
    descriptor = np.float32(descriptor)
    samples = []
    samples.append(descriptor)
    _, result = boost.predict(cv.UMat(np.array(samples)))

    print(result.get())

    im = cv.pyrUp(img)
    samples = []
    for n in range(0, 3):
        for m in range(0, 3):
            cropped = im[int(w / 4 * n):int(w / 4 * (n + 2)), int(h / 4 * m):int(h / 4 * (m +2))]
            cropped = cv.resize(cropped, (600, 400), cv.INTER_AREA)
            samples.append(np.float32(hog.compute(cropped)))
    _, result = boost.predict(cv.UMat(np.array(samples)))
    print(result.get())
                         

if __name__ == '__main__':
    img = cv.imread('test2.png')
    boost_detection(img, "boost.xml")
