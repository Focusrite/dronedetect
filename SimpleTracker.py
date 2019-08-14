# SimpleTracker.py
# Based on/stolen from https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
# Defines the class SimpleTracker which can track multiple objects

import numpy as np
import math
from collections import OrderedDict

class SimpleTracker():
    def __init__(self):

        # Each object that is found has a unique ID
        self.nextObjectID = 0

        # Dictionaries keep track of the coordinates/number
        # of consecutive frames each object has been "lost" in
        self.objects = OrderedDict()
        self.lost_frames = OrderedDict()

        # Number of frames in which an object can be missing
        # before it is considered to have disappeared
        self.max_lost_frames = 25

    # Add a new object to track    
    def register(self, center):
        self.objects[self.nextObjectID] = center
        self.lost_frames[self.nextObjectID] = 0
        self.nextObjectID += 1

    # Remove an object so that we do not track it anymore    
    def deregister(self, objectID):
        del self.objects[objectID]
        del self.lost_frames[objectID]

    # Update the tracker given rectangles in which objects are detected    
    def update(self, rects):
        if len(rects) == 0:
            # If no objects are detected, increase the lost_frames
            # count for all objects and remove those that have been
            # lost for more than max_lost_frames frames
            for objectID in self.lost_frames.keys():
                self.lost_frames[objectID] += 1
                if self.lost_frames[objectID] > self.max_lost_frames:
                    self.deregister(objectID)
            return self.objects

        # Initialize an array to store the center points found
        # in the current frame
        inputCenters = np.zeros((len(rects), 2), dtype = "int")

        #Calculate the center points of each rectangle
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCenters[i] = (cX, cY)
    
        if len(self.objects) == 0:
            # If we aren't currently tracking any objects, simply
            # register all found objects
            for i in range(0, len(inputCenters)):
                self.register(inputCenters[i])
        else:
            # List all objects that are currently being tracked
            objectIDs = list(self.objects.keys())
            objectCenters = list(self.objects.values())

            # Compute a matrix where the distances between each pair
            # of already tracked object and detected object is stored
            D = np.zeros((len(objectCenters), len(inputCenters)), dtype = "float32")
            for i in range(0, len(objectCenters)):
                for j in range(0, len(inputCenters)):
                    D[i, j] = math.sqrt(math.pow(objectCenters[i][0] - inputCenters[j][0], 2) + math.pow(objectCenters[i][1] - inputCenters[j][1], 2))

            # Find the smallest value in each row and sort rows
            rows = D.min(axis = 1).argsort()

            # Find the smallest value in each column and sort columns
            cols = D.argmin(axis = 1)[rows]

            # Sets to keep track of which row and column indexes we
            # have examined
            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    # If the row or column has been examined, ignore it
                    continue

                # Get the object ID, set the new center point and
                # reset the lost_frames counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputCenters[col]
                self.lost_frames[objectID] = 0

                # Mark the row and column as examined
                usedRows.add(row)
                usedCols.add(col)

            # Find the rows and columns we have not yet used    
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # If there are more tracked objects than found objects,
            # check if any have disappeared
            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    objectID = objectIDs[row]
                    self.lost_frames[objectID] += 1

                    if self.lost_frames[objectID] > self.max_lost_frames:
                        self.deregister(objectID)

            else:
                # Otherwise, register the remaining detected objects
                for cl in unusedCols:
                    self.register(inputCenters[col])
            return self.objects            


