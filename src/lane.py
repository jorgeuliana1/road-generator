import math
import numpy as np
import cv2
from roadgraphics import *

class Lane:
    def __init__(self, x0, w, h):
        self.x0 = x0
        # x0 is the upper left vertex of the lane
        self.h, self.w = h, w
        # h and w are height and width

    def getAbsoluteCoordinates(self, x, y):
        # (0, 0) is the center of the lane
        
        # Finding the absolute coordinates of the center:
        xc, yc = self.x0 + self.w // 2, self.h // 2

        # Finding the x and y in absolute coordinates:
        xa, ya = xc + x, yc + y

        return xa, ya

    def insertTemplate(self, layer, template, x, y):
        # x and y are the coordinates related to the center of the template

        # Getting lane x and y:
        xc, yc = self.getAbsoluteCoordinates(x, y)

        # Finding the template insertion vertexes:
        x0, y0, x1, y1 = self.getTemplateCoords(template, dx=x, dy=y)

        # Correcting shift and template dimensions (if necessary):
        template = self.correctDimensions(template, dx=x, dy=y)
        if template is False:
            return False
        x0, y0, x1, y1 = self.correctShift(template, x, y)

        try:

            # Inserting the image:
            new_layer = layer.copy()
            new_layer[y0:y1, x0:x1] = template

            # Returning template location:
            return layer, ((x0, y0), (x1, y1))

        except:
            
            return False

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

    def fits(self, template, dx=0, dy=0):
        template_height, template_width, _ = template.shape
        
        if self.h < template_height or self.w < template_width:
            return False
        
        # dx and dy represent the displacement of the template

        # Getting the absolute points:
        x0, y0, x1, y1 = self.getTemplateCoords(template, dx=dx, dy=dy)

        # Analyzing point by point:
        if x0 < self.x0 or x1 > (self.x0 + self.w):
            return False
        
        if y0 < 0 or y1 > self.h:
            return False

        return True

    def getTemplateCoords(self, template, dx=0, dy=0):
        # dx and dy represent the displacement of the template
        height, width, _ = template.shape

        # Getting relative coordinates:
        rx0 = int(- width/2 + dx)
        ry0 = int(-height/2 + dy)
        rx1 = int(  width/2 + dx)
        ry1 = int( height/2 + dy)

        # Correcting sizes:
        if (height + 2 * dy) % 2 != 0:
            ry0 -= 1
        if (width  + 2 * dx) % 2 != 0:
            rx0 -= 1

        # Getting the absolute coordinates:
        x0, y0 = self.getAbsoluteCoordinates(rx0, ry0)
        x1, y1 = self.getAbsoluteCoordinates(rx1, ry1)

        return x0, y0, x1, y1

    def correct_displacement(self, template, dx, dy):
        x0, y0, x1, y1 = template.bounding_box
        t_w, t_h = x1 - x0, y1 - y0
        x0, y0, x1, y1 = x0 + dx, y0 + dy, x1 + dx, y1 + dy

        # Correcting shift:
        if x1 > self.x0 + self.w:
            x1 = self.x0 + self.w
            x0 = x1 - t_w
        if x0 < self.x0:
            x0 = self.x0
            x1 = x0 + t_w
        if y1 > self.h:
            y1 = self.h
            y0 = y1 - t_h
        if y0 < 0:
            y0 = 0
            y1 = t_h

        return x0, y0, x1, y1


    def correctShift(self, template, dx, dy):

        # LEGACY

        t_h, t_w, _ = template.shape

        x0, y0, x1, y1 = self.getTemplateCoords(template, dx=dx, dy=dy)

        # Correcting shift:
        if x1 > self.x0 + self.w:
            x1 = self.x0 + self.w
            x0 = x1 - t_w
        if x0 < self.x0:
            x0 = self.x0
            x1 = x0 + t_w
        if y1 > self.h:
            y1 = self.h
            y0 = y1 - t_h
        if y0 < 0:
            y0 = 0
            y1 = t_h

        return x0, y0, x1, y1


    def correctDimensions(self, template, dx=0, dy=0):

        # LEGACY
        
        t_h, t_w, _ = template.shape

        x0, y0, x1, y1 = self.getTemplateCoords(template, dx=dx, dy=dy)

        # Correcting dimensions
        if t_w > self.w:
            x0 = self.x0
            x1 = int((self.x0 + self.w) * 0.9)
        if t_h > self.h:
            y0 = 0
            y1 = int(self.h * 0.9)

        # Resizing template
        try:
            template = cv2.resize(template, (x1-x0, y1-y0), interpolation=cv2.INTER_AREA)
            return template
        except:
            return False