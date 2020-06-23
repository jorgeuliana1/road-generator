import itertools
import math
import numpy as np

class MarkTracker:
    __filename   = ""
    __location   = (0, 0, 0, 0)
    __label      = ""
    __dimensions = (0, 0)

    def __init__(self, filename, dimensions):
        self.__filename = filename
        self.__h, self.__w = dimensions

    def __correct_coordinates(self):
        h, w = self.__h, self.__w
        x0, y0, x1, y1 = self.__location

        # Correcting the coordinates:
        if x0 < 0:
            x0 = 0
        if x1 < 0:
            x1 = 0
        if y0 < 0:
            y0 = 0
        if y1 < 0:
            y1 = 0
        if x0 > w:
            x0 = w
        if x1 > w:
            x1 = w
        if y0 > h:
            y0 = h
        if y1 > h:
            y1 = h

        self.__location = x0, y0, x1, y1

    def addLocation(self, location, m_class):
        self.__location = location
        # Location format:
        # (x0, y0, x1, y1)
        self.__label = m_class

    def getString(self):

        # Getting Xs and Ys
        x0, y0, x1, y1 = self.__location

        # Formatting string
        loc_str = str(x0) + "," + str(y0) + "," + str(x1) + "," + str(y1)
        full_st = self.__filename + "," + loc_str + "," + self.__label
        return full_st

    def getLabel(self):
        return self.__label

    def getLocation(self):
        self.__correct_coordinates()
        return self.__location

    def move(self, dx, dy):

        dx, dy = int(dx), int(dy)

        # Getting Xs and Ys
        x0, y0, x1, y1 = self.__location

        # Inserting new values
        self.__location = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)

    def applyPerspective(self, TM, image_dimensions):
        x0, y0, x1, y1 = self.__location

        # X : vector containing every value of x in the border of the bounding box
        # Y : vector containing every value of x in the border of the bounding box

        x_values = np.arange(x0, x1, 1)
        y_values = np.arange(y0, y1, 1)

        left_border_coords = [(x0, yi) for yi in y_values]
        right_border_coords = [(x1, yi) for yi in y_values]
        up_border_coords = [(xi, y0) for xi in x_values]
        down_border_coords = [(xi, y1) for xi in x_values]

        border_coords = left_border_coords + right_border_coords \
            + up_border_coords + down_border_coords

        m = len(border_coords)
        X = np.array([p[0] for p in border_coords])
        Y = np.array([p[1] for p in border_coords])

        # C_original : matrix of the original coordinates

        C_original = np.array([X, Y, np.ones((m), dtype=int)])
        
        # C_perspective : matrix of the coordinates after the perspective was applied
        # X_perspective : X vector after the perspective was applied
        # Y_perspective : Y vector after the perspective was applied

        C_perspective = TM.dot(C_original)
        X_perspective = C_perspective[0,:] / C_perspective[2,:]
        Y_perspective = C_perspective[1,:] / C_perspective[2,:]
        
        x0, y0 = X_perspective.min(), Y_perspective.min()
        x1, y1 = X_perspective.max(), Y_perspective.max()

        self.__location = int(x0), int(y0), int(x1), int(y1)
