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

        h, w = image_dimensions

        x0, y0, x1, y1 = self.__location

        # Applying the perspective to the points
        tw = x1 - x0
        th = y1 - y0
        P = np.array([[0, tw, tw, 0],
                      [0, 0, th, th],
                      [1, 1, 1, 1]])
        O = np.array([[x0, x1],
                      [y0, y1],
                      [1, 1]])

        Pl = np.dot(TM, P)
        Or = np.dot(TM, O)

        newxs = Pl[0, :] / Pl[2, :]
        newys = Pl[1, :] / Pl[2, :]
        oxs = Or[0, :] / Or[2, :]
        oys = Or[1, :] / Or[2, :]
        x0 = oxs.min()
        x1 = oxs.max()
        y0 = oys.min()
        y1 = oys.max()
        minnewxs = newxs.min()
        minnewys = newys.min()
        maxnewxs = newxs.max()
        maxnewys = newys.max()

        nw = int(math.ceil(maxnewxs)) - int(math.floor(minnewxs))
        nh = int(math.ceil(maxnewys)) - int(math.floor(minnewys))

        mark_y_bias = int(x0 - w // 2)
        y_bias_direction = mark_y_bias / abs(mark_y_bias + 0.001)
        y_bias_intensity = y_bias_direction / w
        y_offset = nw * y_bias_intensity * 100
        y_offset = y_offset / np.log(abs(y_offset))

        hnw = (nw / 2)
        hnh = (nh / 2)

        xc = (x0 + x1)/2

        x0 = xc - hnw
        x1 = xc + hnw

        if y_bias_direction > 0:
            x0 -= y_offset
            x1 += y_offset
        elif y_bias_direction < 0:
            x1 -= y_offset
            x0 += y_offset

        self.__location = (int(x0), int(y0), int(x1), int(y1))