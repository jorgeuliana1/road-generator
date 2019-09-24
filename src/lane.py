import math
import numpy as np
import cv2

class Lane:
    h, w = 0, 0
    x0 = 0
    def __init__(self, x0, w, h):
        self.x0 = x0
        # x0 is the upper left vertex of the lane
        self.h, self.w = h, w
        # h and w are height and width
    def getAbsoluteCoordinates(self, x, y):
        # (0, 0) is the center of the lane
        
        # Finding the absolute coordinates of the center:
        xc, yc = (self.x0 + self.h)/2.00, self.w/2.00

        # Finding the x and y in absolute coordinates:
        xa, ya = xc + x, yc + y

        # Rounding:
        if x > 0:
            xa, ya = math.ceil(xa), math.ceil(ya)
        else:
            xa, ya = math.floor(xa), math.floor(ya)

        return xa, ya
    def insertTemplate(self, layer, template, x, y):
        # x and y are the coordinates of the center of the template
        
        # Getting template dimensions:
        t_h, t_w, _ = template.shape

        # Getting lane x and y:
        xc, yc = self.getAbsoluteCoordinates(x, y)

        # Finding the template insertion vertexes:
        x0, x1 = math.floor(xc - t_w/2.00), math.ceil(xc + t_w/2.00)
        y0, y1 = math.floor(yc - t_h/2.00), math.ceil(yc + t_h/2.00)

        # Inserting the image:
        layer[y0:y1, x0:x1] = template

        # Returning template location:
        return ((x0, y0), (x1, y1))