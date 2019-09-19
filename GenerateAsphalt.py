import cv2
import numpy as np
import math


# Experimental values
WIDTH, HEIGHT = 480, 320
IMAGE_COUNT = 0
DIVISIONS = 30
PATH_ASFALTO  = 'asfalto.jpg'
PATH_TEMPLATE = 'template.png'
PATH_WEIRD = 'background.jpg'
ROTATION_DEGREES = -60

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
    # TODO: FIX
    # Setting the block dimensions:
    block_w, block_h = get_block_dimensions(image, divisions)

    # Setting colors
    GREEN = (  0, 255,   0)
    WHITE = (255, 255, 255)

    THICK = 3                # Thickness measured in pixels

    # Inserting the lines at the overlay
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

def generate_empty_templates_layer(dimensions):
    w, h = dimensions
    templates_layer = np.zeros((h, w, 4), np.uint8)
    return templates_layer

def blend_layers(background, foreground):
    added_image = transparent_overlay(background, foreground)
    return added_image

def transparent_overlay(background, foreground):
    h, w, _ = background.shape
    img = generate_empty_templates_layer((w, h))

    for i in range(h):
        for j in range(w):
            alpha = float(foreground[i][j][3] / 255.0)
            img[i][j] = alpha * foreground[i][j] + (1 - alpha) * background[i][j]

    return img

def rotate(image, theta, phi, gamma, dx, dy, dz):
    h, w, _ = image.shape

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

    # Using cv2 to warp the image
    return cv2.warpPerspective(image.copy(), TM, (w, h))
    

# Testing the code:

dimensions = (WIDTH, HEIGHT) # Defining the dimensions
asphalt_bg = get_bg_from_image(dimensions, PATH_ASFALTO) # Defining the bg
weird_bg = get_bg_from_image(dimensions, PATH_WEIRD) # Defining the weird bg
sample_template = get_template_from_image(dimensions, DIVISIONS, PATH_TEMPLATE) # Getting the arrow
templates  = generate_empty_templates_layer(dimensions) # Defining the overlay mask

# simulate_blocks(templates, DIVISIONS) # Painting the overlay mask with the way separation marks
insert_at_block(templates, DIVISIONS, math.floor(DIVISIONS/2), sample_template) # Painting the overlay mask with the arrow

# Joining all the layers
img = blend_layers(asphalt_bg, templates)
simulate_blocks(img, DIVISIONS) # Small workaround, the simulate_blocks ain't working as I wanted

# Warping perspective
rotation_radians = ROTATION_DEGREES/180.00 * math.pi
img = rotate(img, rotation_radians, 0, 0, 0, 0, 0) # Rotating the image in X

img = blend_layers(weird_bg, img)
save_image(img) # Saving the image