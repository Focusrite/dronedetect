import cv2 as cv
import numpy as np
import os
from pypylon import pylon

win_size = (600, 400)
cell_size = (50, 50)
block_size = (100, 100)
block_stride = (50, 50)
nbins = 9
signed_gradients = True
hog = cv.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins, 1, -1, 0, 0.2, 1, 64, False)

feats = []
response = []
predictions = []

no_of_pos = 0
no_of_neg = 0

for filename in os.listdir("positive_samples"):
    if filename.endswith(".png"):
        image = cv.imread("positive_samples/" + filename)
        if image is None:
            break
        descriptor = hog.compute(image)
       # print (descriptor.shape)
        f = descriptor#.reshape(1, -1)
        f = np.float32(f)
        feats.append(f)
        response.append(1)
        no_of_pos = no_of_pos + 1      

for filename in os.listdir("negative_samples"):
    if filename.endswith(".png"):
        image = cv.imread("negative_samples/" + filename)
        descriptor = hog.compute(image)
        #print(descriptor.size)
        f = descriptor#reshape(1, -1)
        f = np.float32(f)
        feats.append(f)
        response.append(-1)
        no_of_neg = no_of_neg + 1

boost = cv.ml.Boost_create()
feats_np = np.asarray(feats)
res_np = np.asarray(response)

print("The length of feats is: ", feats_np.shape)
print("The length of response is: ", res_np.shape)
#print(feats_np)

res_umat = cv.UMat(res_np)
feats_umat = cv.UMat(np.array(feats))



boost = boost.load("boost.xml")
#boost.train(feats_umat, cv.ml.ROW_SAMPLE, res_umat)
#boost.save("boost.xml")

tests = []
no_of_images = 0
for filename in os.listdir("test_samples"):
    if filename.endswith(".png"):
        image = cv.imread("test_samples/" + filename)
        print(filename)
        descriptor = hog.compute(image)
        f = descriptor#.reshape(1, -1)
        f = np.float32(f)
        tests.append(f)
        no_of_images = no_of_images + 1

print(no_of_images)        
_, result = boost.predict(cv.UMat(np.array(tests)))
print(result.get().shape)
print(result.get())
