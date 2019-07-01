import numpy as np
from collections import OrderedDict

class SimpleTracker():
    def __init__(self):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.lost_frames = OrderedDict()
        self.max_lost_frames = 25

    def register(self, center):
        self.objects[self.nextObjectID] = center
        self.lost_frames[self.nextObjectID] = 0
        self.nextObjectID += 1
        print("Adding object to track")

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.lost_frames[objectID]
        print("Removing object to track")

    def update(self, rects):
        if len(rects) == 0:
            for objectID in self.lost_frames.keys():
                self.lost_frames[objectID] += 1
                if self.lost_frames[objectID] > self.max_lost_frames:
                    self.deregister(objectID)
            return self.objects
        inputCenters = np.zeros((len(rects), 2), dtype = "int")

        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCenters[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(0, len(inputCenters)):
                self.register(inputCenters[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCenters = list(self.objects.values())

            D = np.zeros((len(objectCenters), len(inputCenters)), dtype = "float32")
            rows = D.min(axis = 1).argsort()
            cols = D.argmin(axis = 1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue

                objectID = objectIDs[row]
                self.objects[objectID] = inputCenters[col]
                self.lost_frames[objectID] = 0

                usedRows.add(row)
                usedCols.add(col)

                unusedRows = set(range(0, D.shape[0])).difference(usedRows)
                unusedCols = set(range(0, D.shape[1])).difference(usedCols)

                if D.shape[0] >= D.shape[1]:
                    for row in unusedRows:
                        objectID = objectIDs[row]
                        self.lost_frames[objectID] += 1

                        if self.lost_frames[objectID] > self.max_lost_frames:
                            self.deregister(objectID)

                else:
                     for cl in unusedCols:
                         self.register(inputCenters[col])
            return self.objects            

simpleTracker = SimpleTracker()
rects = []

