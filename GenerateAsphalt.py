import cv2
import numpy as np
import math


# Experimental values
WIDTH, HEIGHT = 480, 320
IMAGE_COUNT = 0
DIVISIONS = 3
PATH_ASFALTO  = 'asfalto.jpg'
PATH_TEMPLATE = 'template.png'

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image):
    count = 0
    cv2.imwrite('image_'+str(count)+'.jpg', image)

def get_block_dimensions(image, divisions):
    h, w, alpha = image.shape
    block_w = math.floor(w/divisions)
    block_h = h
    return block_w, block_h

def simulate_blocks(image, divisions):
    # Setting the block dimensions:
    block_w, block_h = get_block_dimensions(image, divisions)

    # Setting colors
    GREEN = (  0, 255,   0)
    WHITE = (255, 255, 255)

    THICK = 3                # Thickness measured in pixels

    # Inserting the lines at the image
    for i in range(1, divisions):
        pos1 = (block_w * i, 0)          # Beggining of the line
        pos2 = (block_w * i, block_h)    # End of the line

        cv2.line(image, pos1, pos2, WHITE, THICK)

def insert_at_block(image, divisions, block_to_add, template):
    # Finding the block limits
    image_h, image_w, image_c = image.shape
    block_width = math.ceil(image_w / divisions)
    block_ul = (block_width * (block_to_add - 1), 0) # Upper left limit of the block
    block_dr = (block_width * block_to_add, image_h) # Down right limit of the block

    # cv2.line(image, block_ul, block_dr, (255, 255, 255), 3) # For experimental purposes only

    # Finding the block mean point
    ul_x, ul_y = block_ul
    dr_x, dr_y = block_dr

    mpoint = ((ul_x + dr_x)/2, (ul_y + dr_y)/2) # Creating the mean point as a tuple
    mpoint_x, mpoint_y = mpoint

    # Finding the template dimensions
    t_h, t_w, t_c = template.shape

    # Finding the insertion points
    insertion_ul = (math.ceil(mpoint_x - t_w/2), math.ceil(mpoint_y - t_h/2))
    insertion_dr = (math.ceil(mpoint_x + t_w/2), math.ceil(mpoint_y + t_h/2))
    iul_x, iul_y = insertion_ul
    idr_x, idr_y = insertion_dr

    # cv2.line(image, insertion_ul, insertion_dr, (255, 255, 255), 3) # For experimental purposes only

    # Inserting the image at the points
    image[iul_y:idr_y, iul_x:idr_x] = template

def get_bg_from_image(dimensions, image_path):
    WIDTH, HEIGHT = dimensions
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Convert the image from RGB2RGBA
    if len(img.shape) > 2 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    return cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)

def get_template_from_image(dimensions, divisions, image_path):
    unchanged_template = cv2.imread(PATH_TEMPLATE, cv2.IMREAD_UNCHANGED)
    th, tw, ta = unchanged_template.shape # Original template dimensions
    w, h = dimensions # Background dimensions
    
    # Getting the image ratio
    smaller = th
    bigger  = tw
    if tw < th:
        smaller = tw
        bigger  = th
    ratio = smaller / bigger

    # Resized image dimensions
    template_w = math.floor(0.9 * w / divisions)
    template_h = math.floor(template_w * ratio)

    # Getting template
    template_dim = (template_h, template_w)
    template = cv2.resize(unchanged_template, template_dim, interpolation=cv2.INTER_AREA)
    return template

bg = get_bg_from_image((WIDTH, HEIGHT), PATH_ASFALTO) # Sample background
template = get_template_from_image((WIDTH, HEIGHT), DIVISIONS, PATH_TEMPLATE)
simulate_blocks(bg, DIVISIONS)
insert_at_block(bg, DIVISIONS, math.floor(DIVISIONS/2), template)
save_image(bg)

# TODO: Find out why it only works with square images