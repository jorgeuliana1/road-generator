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

        # Defining the points:
        # UR : Up-right point
        # UL : Up-left point
        # DR : Down-right point
        # DL : Down-left point
        x0, y0, x1, y1 = self.__location
        ur = np.array([x0, y0, 1])
        ul = np.array([x1, y0, 1])
        dr = np.array([x0, y1, 1])
        dl = np.array([x1, y1, 1])

        # 2D to 3D
        A1 = np.array([[1, 0, -w/2],
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

        hnw = (nw / 2)*1.2
        hnh = (nh / 2)*1.2

        xc = (x0 + x1)/2

        x0 = xc - hnw
        x1 = xc + hnw

        self.__location = (int(x0), int(y0), int(x1), int(y1))