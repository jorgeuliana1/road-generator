import math
import numpy as np
import cv2

class Lane:
    def __init__(self, x0, w, h):
        self.x0 = x0
        # x0 is the upper left vertex of the lane
        self.h, self.w = h, w
        # h and w are height and width
    def getAbsoluteCoordinates(self, x, y):
        # (0, 0) is the center of the lane
        
        # Finding the absolute coordinates of the center:
        xc, yc = self.x0 + self.w/2.00, self.h/2.00

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
        x0, x1 = math.floor(xc - t_w/2.00), math.floor(xc + t_w/2.00)
        y0, y1 = math.floor(yc - t_h/2.00), math.floor(yc + t_h/2.00)

        # Adding the shift:
        y0 += y
        y1 += y
        x0 += x
        x1 += x

        # Correcting shift:
        if x1 > self.x0 + self.w:
            x1 = self.x0 + self.w
        if x0 < self.x0:
            x0 = self.x0
        if y1 > self.h:
            y1 = self.h
        if y0 < 0:
            y0 = 0

        # Inserting the image:
        new_layer = layer.copy()
        new_layer[y0:y1, x0:x1] = template

        # Returning template location:
        return new_layer, ((x0, y0), (x1, y1))
    def drawSeparator(self, layer, right_limit, left_limit, width=3, color=(255, 255, 255), dotted=False, dot_size=3, dot_distance=1, x_dist=0):
        height = self.h # For code simplification
        new_layer = layer.copy()

        # Getting the layer's dimensions
        h, w, _ = layer.shape

        # Creating the line overlayer:
        overlay = np.zeros([h, w, 3], dtype=np.uint8)

        # Defining the alpha channel
        blue, green, red = cv2.split(overlay)
        alpha = np.zeros(blue.shape, dtype=blue.dtype)
        overlay = cv2.merge((blue, green, red, alpha))

        # Defining the pixel to be inserted at the layer
        r, g, b = color # The default color is white
        pixel = np.zeros([1, 1, 3], dtype=np.uint8)
        blue, green, red = cv2.split(pixel)
        alpha = np.ones(blue.shape, dtype=blue.dtype) * 255
        blue.fill(b)
        red.fill(r)
        green.fill(g)
        pixel = cv2.merge((blue, green, red, alpha))

        dot_counter = 0

        # Painting the layer:
        for j in range(0, height):
            dot_counter+=1
            if dotted and dot_counter > dot_size:
                dot_counter = 0 - dot_distance
            if dot_counter >= 0:
                overlay[j][left_limit:right_limit] = pixel
        
        return new_layer + overlay
    def drawRightSeparator(self, layer, width=3, color=(255, 255, 255), dotted=False, dot_size=3, dot_distance=1, x_dist=0):
        right_limit = self.x0 + self.w - x_dist
        left_limit = right_limit - width
        return self.drawSeparator(layer, right_limit, left_limit, width=width, color=color, dotted=dotted, dot_size=dot_size, dot_distance=dot_distance, x_dist=x_dist)
    def drawLeftSeparator(self, layer, width=3, color=(255, 255, 255), dotted=False, dot_size=3, dot_distance=1, x_dist=0):
        left_limit = self.x0 + x_dist
        right_limit = left_limit + width
        return self.drawSeparator(layer, right_limit, left_limit, width=width, color=color, dotted=dotted, dot_size=dot_size, dot_distance=dot_distance, x_dist=x_dist)
