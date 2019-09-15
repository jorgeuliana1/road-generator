import cv2
import numpy as np
import math

HEIGHT, WIDTH = 480, 480 # DEFAULT VALUES
IMAGE_COUNT = 0
DIVISIONS = 7
PATH_ASFALT0  = 'asfalto.jpg'
PATH_TEMPLATE = 'template.png'

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image):
    count = 0
    cv2.imwrite('image_'+str(count)+'.jpg', image)

def get_block_dimensions(image, divisions):
    w, h, alpha = image.shape
    block_w = math.floor(w/divisions)
    block_h = h
    return block_w, block_h

def simulate_blocks(image, divisions):
    # Setting the block dimensions:
    block_w, block_h = get_block_dimensions(image, divisions)

    # Setting colors
    green = (  0, 255,   0)
    white = (255, 255, 255)

    thickness = 3                # Thickness measured in pixels

    # Inserting the lines at the image
    for i in range(1, divisions):
        pos1 = (block_w * i, 0)          # Beggining of the line
        pos2 = (block_w * i, block_h)    # End of the line

        cv2.line(image, pos1, pos2, white, thickness)

def insert_at_block(image, divisions, block_to_add, template):
    # Setting the general block dimensions
    block_w, block_h = get_block_dimensions(image, divisions)

    # Setting the specific block dimensions
    underlimit_x, overlimit_x = (block_to_add) * block_w, (block_to_add + 1) * block_w

    # Getting the block center (FOR TESTING PURPOSES ONLY)
    center_x = math.floor((underlimit_x + overlimit_x)/2)
    center_y = math.floor(block_h/2)

    # SOME TROUBLES HERE
    # TODO: FIX
    # Inserting the template at the center of the block (FOR TESTING PURPOSES ONLY)
    template_w, template_h, template_alpha = template.shape
    x_offset = center_x #- math.floor(template_w/2)
    y_offset = center_y - math.floor(template_h/2)
    image[y_offset:y_offset+template_w, x_offset:x_offset+template_h] = template

def get_bg_from_image(dimensions, image_path):
    HEIGHT, WIDTH = dimensions
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Convert the image from RGB2RGBA
    if len(img.shape) > 2 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    return cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)

def get_template_from_image(dimensions, divisions, image_path):
    unchanged_template = cv2.imread(PATH_TEMPLATE, cv2.IMREAD_UNCHANGED)
    tw, th, ta = unchanged_template.shape # Original template dimensions
    w, h = dimensions # Background dimensions
    ratio = th / tw # Original image ratio

    # Resized image dimensions
    template_w = math.floor(0.9 * w/divisions)
    template_h = math.floor(template_w * ratio)

    # Getting template
    template_dim = (template_h, template_w)
    template = cv2.resize(unchanged_template, template_dim, interpolation=cv2.INTER_AREA)
    return template

bg = get_bg_from_image((HEIGHT, WIDTH), 'asfalto.jpg') # Sample background
template = get_template_from_image((HEIGHT, WIDTH), DIVISIONS, PATH_TEMPLATE)
simulate_blocks(bg, DIVISIONS)
insert_at_block(bg, DIVISIONS, 5, template)
insert_at_block(bg, DIVISIONS, 3, template)
save_image(bg)

# TODO: Find out why it only works with square images