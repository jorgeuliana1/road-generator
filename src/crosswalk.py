import cv2
import numpy as np

class CrossWalk:
    __bar_w   = 4
    __bar_h   = 64
    __spacing = 4

    def __init__(self, bars):
        self.__bars   = bars
        self.__width  = int(self.__bar_w * bars + self.__spacing * bars)
        self.__height = self.__bar_h

        def CreatePixel():
            # Defining the pixel to be inserted at the bar
            color = (255, 255, 255)
            r, g, b = color # The default color is white
            pixel = np.zeros([1, 1, 3], dtype=np.uint8)
            blue, green, red = cv2.split(pixel)
            alpha = np.ones(blue.shape, dtype=blue.dtype) * 255
            blue.fill(b)
            red.fill(r)
            green.fill(g)
            pixel = cv2.merge((blue, green, red, alpha))

            return pixel

        def CreateBar(self):
            h, w = self.__bar_h, self.__bar_w
            
            bimg = np.zeros((h, w, 4), np.uint8) # BGRA image
            
            # Filling with white:
            pixel = CreatePixel()
            bimg[0:h, 0:w] = pixel

            return bimg

        def CreateTemplate(self):
            h, w = self.__height, self.__width
            template = np.zeros((h, w, 4), np.uint8) # BGRA image

            bar = CreateBar(self)

            for i in range(0, self.__bars):
                j = i + 1

                # Getting bar positions:
                x0 = i * self.__bar_w + i * self.__spacing + int(self.__spacing / 2)
                x1 = x0 + self.__bar_w
                y0 = 0
                y1 = self.__bar_h

                # Inserting at template:
                template[y0:y1, x0:x1] = bar

            self.__template = template
        
        CreateTemplate(self)

    def get(self):
        return self.__template