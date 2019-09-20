import numpy as np
import math
import cv2

def get_block_dimensions(image, divisions):
    h, w, alpha = image.shape
    block_w = math.floor(w/divisions)
    block_h = h
    return block_w, block_h

def draw_straight_line(image, pos1, pos2, color, thickness):
    x1, y1 = pos1
    x2, y2 = pos2

    # Applying thickness:
    x1 -= thickness
    x2 += thickness
    
    # Rectangle starting at:
    origin = (x1, y1)

    # Rectangle ending at:
    destiny = (x2, y2)

    # Getting image dimensions:
    h, w, _ = image.shape

    # Creating the line overlayer:
    overlay = np.zeros([h, w, 3], dtype=np.uint8)

    # Defining the alpha channel
    blue, green, red = cv2.split(overlay)
    alpha = np.zeros(blue.shape, dtype=blue.dtype)
    overlay = cv2.merge((blue, green, red, alpha))

    # Creating a pixel of the specified color
    r, g, b = color
    pixel = np.zeros([1, 1, 3], dtype=np.uint8)
    blue, green, red = cv2.split(pixel)
    alpha = np.ones(blue.shape, dtype=blue.dtype) * 255
    blue.fill(b)
    red.fill(r)
    green.fill(g)
    pixel = cv2.merge((blue, green, red, alpha))

    # "Painting" the image
    for i in range(x1, x2):
        for j in range(y1, y2):
            overlay[j][i] = pixel

    image+=overlay

def simulate_blocks(image, divisions, color, thickness):
    # Setting the block dimensions:
    block_w, block_h = get_block_dimensions(image, divisions)

    # Inserting the lines at the overlay
    for i in range(1, divisions):
        pos1 = (block_w * i, 0)          # Beggining of the line
        pos2 = (block_w * i, block_h)    # End of the line

        draw_straight_line(image, pos1, pos2, color, thickness)

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
    unchanged_template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
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

def bring_to_bottom(image):
    # This function brings the template to the bottom of the image

    # Getting image dimensions
    h, w, _ = image.shape

    # Creating empty template
    new_image = generate_empty_templates_layer((w, h))

    # Defining a empty line
    empty_line = np.zeros((1, w, 4), dtype=np.uint8)

    # Counting the amount of lines to go down
    lines = h
    counter = 0
    for i in range(lines):

        a1 = image[:][h - i - 1]
        a2 = empty_line[:][0]

        # Verifying if the lines are equal
        equality = np.sum(np.all(np.equal(a1, a2)))

        if equality:
            counter+= 1
        else:
            break

    # Redrawing the image:
    new_image[:][counter:h] = image[:][0:h-counter]

    return new_image, counter