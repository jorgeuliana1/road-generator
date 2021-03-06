import numpy as np
import math, os, cv2

def get_bg_from_image(dimensions, image_path):
    WIDTH, HEIGHT = dimensions
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Convert the image from RGB2RGBA
    if len(img.shape) > 2 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    return cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)

def load_image(dimensions, image_path):
    WIDTH, HEIGHT = dimensions
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Convert the image from RGB2RGBA
    if len(img.shape) > 2 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    return cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)

def get_template_from_image(dimensions, image_path):
    template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    h, w, _ = template.shape
    
    # DETERMINING THE USEFUL AREA OF THE IMAGE:
    # GS_TEMPLATE : GRAYSCALE TEMPLATE
    black_template = cv2.bitwise_not(template)
    gs_template = cv2.cvtColor(black_template, cv2.COLOR_BGR2GRAY)
    gs_template = 255*(gs_template < 128).astype(np.uint8)
    coords = cv2.findNonZero(gs_template)
    x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
    old_template = template
    template = template[y:y+h, x:x+w]

    template = cv2.resize(template, (h, w), interpolation=cv2.INTER_AREA)

    return template

def generate_empty_templates_layer(dimensions):
    w, h = dimensions
    templates_layer = np.zeros((h, w, 4), np.uint8)
    return templates_layer

def blend(background, foreground):
    added_image = transparent_overlay(background, foreground)
    return added_image

def transparent_overlay(background, foreground):
    h, w, _ = background.shape
    img = generate_empty_templates_layer((w, h))
    background_alpha = np.array(background[:,:,3])
    alpha_matrix_base = np.array(foreground[:, :, 3] / 255.0).T
    alpha_matrix = np.array([alpha_matrix_base, alpha_matrix_base, alpha_matrix_base, alpha_matrix_base]).T
    img[:,:] = np.multiply(foreground[:,:], alpha_matrix) + np.multiply(background[:,:], 1 - alpha_matrix)
    img[:,:,3] = background_alpha

    return img

def get_transformation_matrix(image_shape, theta, phi, gamma, dx, dy, dz):
    h, w = image_shape

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
    
    return TM

def rotate(image, TM):
    h, w, _ = image.shape

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

def draw_bbox(image, location, color):
    # Getting Xs and Ys:
    x0, y0, x1, y1 = location
    cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)

def resize_template(template, new_h, new_w):
    old_area = template.shape[0] * template.shape[1]
    new_area = new_h * new_w
    if old_area > new_area:
        return cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        return cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

def apply_color_distortions(img, bright, contrast):
    alpha = 1 + 2 * contrast
    beta  = 100 * bright
    new_image = np.clip(alpha * img + beta, 0, 255).astype('uint8')

    return new_image

def apply_blur(img, blur):
    out = cv2.GaussianBlur(img, (int(blur), int(blur)), 0)
    return out

def blur_borders(img):
    blur = 1
    return cv2.GaussianBlur(img, (int(blur), int(blur)), 0)

def age_layer(layer, age_matrix):

    lh, lw, _ = layer.shape
    new_layer = layer
    new_layer[:,:,3] = np.multiply(1 - age_matrix, layer[:,:,3])

    return new_layer

def load_templates(path, dimensions):
    files = os.listdir(path)
    templates = {}

    for filename in files:
        full_path = os.path.join(path, filename)
        template_name = os.path.splitext(filename)[0]

        template = get_template_from_image(dimensions, full_path)
        templates[template_name] = template

    # This function returns a dict containing the templates.
    return templates