import math
import numpy as np

class MarkTracker:
    __filename = ""
    __location = (0, 0, 0, 0)
    __label    = ""

    def __init__(self, filename):
        self.__filename = filename

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
        return self.__location

    def move(self, dx, dy):

        dx, dy = int(dx), int(dy)

        # Getting Xs and Ys
        x0, y0, x1, y1 = self.__location

        # Inserting new values
        self.__location = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)

    def applyPerspective(self, theta, phi, gamma, dx, dy, dz, image_dimensions):

        h, w = image_dimensions

        d = np.sqrt(h**2 + w**2)
        focal = d / (2 * np.sin(gamma) if np.sin(gamma) != 0 else 1)
        dz = focal
        f = focal

        # 2D to 3D
        A1 = np.array([[1,    0, -w/2],
                    [0,    1, -h/2],
                    [0,    0,    1],
                    [0,    0,    1]])

        # Rotating X, Y and Z
        RX = np.array([[1, 0, 0, 0],
                    [0, np.cos(theta), -np.sin(theta), 0],
                    [0, np.sin(theta), np.cos(theta), 0],
                    [0, 0, 0, 1]])

        RY = np.array([[np.cos(phi), 0, -np.sin(phi), 0],
                    [0, 1, 0, 0],
                    [np.sin(phi), 0, np.cos(phi), 0],
                    [0, 0, 0, 1]])

        RZ = np.array([[np.cos(gamma), -np.sin(gamma), 0, 0],
                    [np.sin(gamma), np.cos(gamma), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

        # Composing R matrix
        R = np.dot(np.dot(RX, RY), RZ)
        # Translation matrix
        T = np.array([[1, 0, 0, dx],
                    [0, 1, 0, dy],
                    [0, 0, 1, dz],
                    [0, 0, 0, 1]])
        # Converting 3D to 2D again
        A2 = np.array([[f, 0, w/2, 0],
                    [0, f, h/2, 0],
                    [0, 0, 1, 0]])

        # Final transformation matrix
        TM = np.dot(A2, np.dot(T, np.dot(R, A1)))

        # Preparing to apply the transformation in the points:
        x0, y0, x1, y1 = self.__location
        p1 = np.array([x0, y0, f])
        p2 = np.array([x1, y1, f])

        # Applying the transformation:
        p1 = np.dot(p1, TM)
        p2 = np.dot(p2, TM)

        x0, y0, _ = p1
        x1, y1, _ = p2

        self.__location = int(x0/w), int(y0/h), int(x1/w), int(y1/h)