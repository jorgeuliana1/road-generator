import numpy as np
import math
import cv2

def get_bg_from_image(dimensions, image_path):
    WIDTH, HEIGHT = dimensions
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Convert the image from RGB2RGBA
    if len(img.shape) > 2 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    return cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)

def get_template_from_image(dimensions, image_path):
    template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    h, w, _ = template.shape
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

def draw_bbox(image, location, color):
    # Getting Xs and Ys:
    x0, y0, x1, y1 = location
    cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)

def resize_template(template, new_h, new_w):
    return cv2.resize(template, (new_h, new_w), interpolation=cv2.INTER_AREA)

def apply_color_distortions(img, bright, contrast):
    new_image = np.zeros(img.shape, img.dtype)
    alpha = 1 + 2 * contrast
    beta  = 100 * bright
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            for c in range(img.shape[2]):
                new_image[y,x,c] = np.clip(alpha*img[y,x,c] + beta, 0, 255)

    return new_image

def apply_blur(img, blur):
    out = cv2.medianBlur(img, int(blur))
    return out

def age_layer(layer, age_matrix):
    def age(layer, age_coef, x0, y0, x1, y1):
        b, g, r, a = cv2.split(layer)
        h, w = a.shape

        for i in range(y0, y1):
            for j in range(x0, x1):
                a[i][j] = a[i][j] * age_coef

        layer = cv2.merge((b, g, r, a))
        return layer

    lh, lw, _ = layer.shape
    mh, mw = len(age_matrix), len(age_matrix[0])
    h, w = math.floor(lh/mh), math.floor(lw/mw)
    nlayer = layer.copy()

    for i in range(0, mh):
        for j in range(0, mw):
            x0, x1 = j * w, (j + 1) * w
            y0, y1 = i * h, (i + 1) * h

            age_coef = age_matrix[i][j] / 100
            nlayer = age(nlayer, age_coef, x0, y0, x1, y1)

    return nlayer


