import cv2
import numpy as np
import math
from road_generator import *
import json
import os

IMAGE_COUNT = 0

# BGR
GREEN =  (  0, 255,   0)
WHITE =  (255, 255, 255)
YELLOW = (255, 255,   0)

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image, title="", path="image.jpg"):
    cv2.imwrite(title+path, image)

def get_parameters(settings_path):

    # Opening the JSON file:
    with open(settings_path, 'r') as f:
        json_file = json.load(f)

    # Getting the dimensions:
    dimensions = (int(json_file["IMAGE_DIMENSIONS"]["WIDTH"]), int(json_file["IMAGE_DIMENSIONS"]["HEIGHT"]))

    # Getting the road settings:
    divisions = int(json_file["ROAD_SETTINGS"]["DIVISIONS"])
    line_thickness = int(json_file["ROAD_SETTINGS"]["LINE_THICKNESS"])
    road = {"DIVISIONS" : divisions, "THICKNESS" : line_thickness}

    # Getting the files paths:
    ground_texture = json_file["PATHS"]["GROUND_TEXTURE"]
    template = json_file["PATHS"]["TEMPLATE"]
    bg = json_file["PATHS"]["BACKGROUND_IMAGE"]
    destiny = json_file["PATHS"]["SAVE_PATH"]
    templates = json_file["PATHS"]["TEMPLATES"]
    paths = {"GROUND" : ground_texture, "TEMPLATE" : template, "BACKGROUND" : bg, "DESTINY" : destiny, "TEMPLATES" : templates}

    # Getting the rotation:
    x = float(json_file["IMAGE_ROTATION"]["X_ROTATION"])
    y = float(json_file["IMAGE_ROTATION"]["Y_ROTATION"])
    z = float(json_file["IMAGE_ROTATION"]["Z_ROTATION"])
    rotation = (x, y, z)

    return dimensions, road, paths, rotation

def location_after_perspective(location, rotation_radians):
    # Getting Xs and Ys:
    pos0, pos1 = location
    x0, y0 = pos0
    x1, y1 = pos1

    # Putting points in cartesian coordinates
    ref_x = (x0 + x1) / 2
    ref_y = (y0 + y1) / 2
    x0, x1 = x0 - ref_x, x1 - ref_x
    y0, y1 = y0 - ref_y, y1 - ref_y

    # Converting to 3D points
    # pos0 = (x0, y0, 0)
    # pos1 = (x1, y1, 0)
    # The rotation must follow the rule:
    # z ** 2 + y ** 2 = y0 ** 2
    # Thus:
    # z = y0*cos(radians)
    # y = y0*sin(radians)

    # Doing the rotation:
    pos0 = (x0, y0*math.cos(rotation_radians), y0*math.sin(rotation_radians))
    pos1 = (x1, y1*math.cos(rotation_radians), y1*math.sin(rotation_radians))

    # Converting to 2D:
    x0, y0, _ = pos0
    x1, y1, _ = pos1
    x0, y0 = x0 * 2.4 + ref_x, y0 * 1.2 + ref_y # Returning to default coordinates
    x1, y1 = x1 * 2.4 + ref_x, y1 * 1.2 + ref_y # Returning to default coordinates
    pos0 = (int(x0), int(y0))
    pos1 = (int(x1), int(y1))

    new_location = (pos0, pos1)
    
    return new_location

def draw_bbox(image, location, color):
    # Getting Xs and Ys:
    pos0, pos1 = location
    x0, y0 = pos0
    x1, y1 = pos1

    cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)

def load_templates(path, dimensions, divisions):
    files = os.listdir(path)
    templates = {}
    
    for filename in files:
        full_path = path + "/" + filename
        template_name = filename.split(".")[0]

        template = get_template_from_image(dimensions, divisions, full_path)
        templates[template_name] = template

    # This function returns a dict containing the templates.
    return templates

# Testing the code:

# Setting the parameters
DIMENSIONS, ROAD, PATHS, ROTATION = get_parameters("settings.json")
WIDTH, HEIGHT = DIMENSIONS
DIVISIONS = ROAD["DIVISIONS"]
LINE_THICKNESS = ROAD["THICKNESS"]
PATH_ASFALTO = PATHS["GROUND"]
PATH_TEMPLATE = PATHS["TEMPLATE"]
PATH_WEIRD = PATHS["BACKGROUND"]
PATH_DESTINY = PATHS["DESTINY"]
TEMPLATES = PATHS["TEMPLATES"]
ROTATION_DEGREES, _, _ = ROTATION

templates_dict = load_templates(TEMPLATES, DIMENSIONS, DIVISIONS)

dimensions = (WIDTH, HEIGHT) # Defining the dimensions
asphalt_bg = get_bg_from_image(dimensions, PATH_ASFALTO) # Defining the bg
weird_bg = get_bg_from_image(dimensions, PATH_WEIRD) # Defining the weird bg
sample_template = templates_dict["RETORNODIREITA"] # Just a sample template
templates = generate_empty_templates_layer(dimensions) # Defining the overlay mask

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
template_location = location_after_perspective(template_location, rotation_radians)
pos0, pos1 = template_location
x0, y0 = pos0
x1, y1 = pos1
y0 += y_update
y1 += y_update
pos0 = (x0, y0)
pos1 = (x1, y1)
template_location = (pos0, pos1)
img = blend(weird_bg, img)
draw_bbox(img, template_location, (0, 0, 255))
save_image(img, path=PATH_DESTINY) # Saving the image