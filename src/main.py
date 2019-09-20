import cv2
import numpy as np
import math
from road_generator import *


# Experimental values
WIDTH, HEIGHT = 480, 320
IMAGE_COUNT = 0
DIVISIONS = 3
PATH_ASFALTO  = 'asphalt_textures/asphalt_001.jpg'
PATH_TEMPLATE = 'templates/template_001.png'
PATH_WEIRD = 'backgrounds/bg_001.jpg'
ROTATION_DEGREES = -60
LINE_THICKNESS = 3

# BGR
GREEN =  (  0, 255,   0)
WHITE =  (255, 255, 255)
YELLOW = (255, 255,   0)

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image, title="image_"):
    count = 0
    cv2.imwrite(title+str(count)+'.jpg', image)

# Testing the code:

dimensions = (WIDTH, HEIGHT) # Defining the dimensions
asphalt_bg = get_bg_from_image(dimensions, PATH_ASFALTO) # Defining the bg
weird_bg = get_bg_from_image(dimensions, PATH_WEIRD) # Defining the weird bg
sample_template = get_template_from_image(dimensions, DIVISIONS, PATH_TEMPLATE) # Getting the arrow
templates  = generate_empty_templates_layer(dimensions) # Defining the overlay mask

draw_ways(templates, DIVISIONS, YELLOW, LINE_THICKNESS) # Painting the overlay mask with the way separation marks

# Painting the overlay mask with the arrow:
template_location = insert_template(templates, DIVISIONS, math.floor(DIVISIONS/2), sample_template)

# Joining all the layers
img = blend(asphalt_bg, templates)

# Warping perspective
rotation_radians = ROTATION_DEGREES/180.00 * math.pi
img = rotate(img, rotation_radians, 0, 0, 0, 0, 0) # Rotating the image in X
img, y_update = bring_to_bottom(img) # Bringing template to bottom

# Updating the template location
# (Don't work as expected yet, it still need to calculate the position change due to the perspective warp)
pos0, pos1 = template_location
x0, y0 = pos0
x1, y1 = pos1
y0 += y_update
y1 += y_update
pos0 = (x0, y0)
pos1 = (x1, y1)
template_location = (pos0, pos1)

img = blend(weird_bg, img)
save_image(img) # Saving the image