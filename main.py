import cv2
import numpy as np
import math
from road_generator import *


# Experimental values
WIDTH, HEIGHT = 480, 320
IMAGE_COUNT = 0
DIVISIONS = 3
PATH_ASFALTO  = 'asfalto.jpg'
PATH_TEMPLATE = 'template.png'
PATH_WEIRD = 'background.jpg'
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

simulate_blocks(templates, DIVISIONS, YELLOW, LINE_THICKNESS) # Painting the overlay mask with the way separation marks
insert_at_block(templates, DIVISIONS, math.floor(DIVISIONS/2), sample_template) # Painting the overlay mask with the arrow

# Joining all the layers
img = blend_layers(asphalt_bg, templates)

# Warping perspective
rotation_radians = ROTATION_DEGREES/180.00 * math.pi
img = rotate(img, rotation_radians, 0, 0, 0, 0, 0) # Rotating the image in X
img, _ = bring_to_bottom(img) # Bringing template to bottom

img = blend_layers(weird_bg, img)
save_image(img) # Saving the image