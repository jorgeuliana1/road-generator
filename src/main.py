import cv2
import numpy as np
import math
import json
import os
from mark_tracker import MarkTracker
from road import Road
from roadimage import RoadImage
from roadgraphics import *

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image, title="", path="image.jpg"):
    cv2.imwrite(title+path, image)

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

def main():
    # Defining colors:
    RED   =  (  0,   0, 255)
    GREEN =  (  0, 255,   0)
    WHITE =  (255, 255, 255)
    YELLOW = (255, 255,   0)

    # Opening the JSON file:
    settings_path = "settings.json" # To change later
    with open(settings_path, 'r') as f:
        json_file = json.load(f)

    # Getting the parameters from the JSON file:

    WIDTH = json_file["IMAGE_DIMENSIONS"]["WIDTH"]
    HEIGHT = json_file["IMAGE_DIMENSIONS"]["HEIGHT"]

    ROAD_LANES = json_file["ROAD_SETTINGS"]["DIVISIONS"]
    LINE_THICKNESS = json_file["ROAD_SETTINGS"]["LINE_THICKNESS"]
    LANE_VARIATION = json_file["ROAD_SETTINGS"]["VARIATION"]

    IMAGE_ROTATION = json_file["IMAGE_ROTATION"]
    MIN_X, MAX_X = IMAGE_ROTATION["MIN_X"], IMAGE_ROTATION["MAX_X"]
    MIN_Y, MAX_Y = IMAGE_ROTATION["MIN_Y"], IMAGE_ROTATION["MAX_Y"]
    MIN_Z, MAX_Z = IMAGE_ROTATION["MIN_Z"], IMAGE_ROTATION["MAX_Z"]

    PATHS = json_file["PATHS"]
    GROUND_TEXTURE = PATHS["GROUND_TEXTURE"]
    TEMPLATES = PATHS["TEMPLATES"]
    BACKGROUNDS = PATHS["BACKGROUND_IMAGE"]
    DESTINY = PATHS["SAVE_PATH"]

    # TODO: Add MARK_POS variation here

    SEED = json_file["SEED"]

    # Loading the roadmarks templates:
    templates = load_templates(TEMPLATES, (WIDTH, HEIGHT), ROAD_LANES)
    # TODO: Load ground textures folder
    ground_textures = 0 # Must change
    # TODO: Load background images folder
    backgrounds = 0 # Must change

    # Loading specific ground texture file:
    ground_texture = get_bg_from_image((WIDTH, HEIGHT), GROUND_TEXTURE)

    # Loading specific background image file:
    bg_img = get_bg_from_image((WIDTH, HEIGHT), BACKGROUNDS)

    # Generating the templates layer:
    overlay = generate_empty_templates_layer((WIDTH, HEIGHT))

    # Creating the image
    img = RoadImage((WIDTH, HEIGHT), DESTINY, backgrounds, ground_textures, templates)
    img.setSeed(SEED)

    # Defining the lanes in the road
    img.defineLanes(ROAD_LANES, LANE_VARIATION)

    road = img.getRoad()
    # Inserting the lanes divisions in the road:
    for i in range(1, ROAD_LANES):
        if i > 0:
            overlay = road.drawSeparator(i - 1, overlay)
    
    # Inserting random template:
    template_class = img.randomMark()
    sample_template = templates[template_class]
    lane_index = img.getRandomLane()
    overlay, template_location = road.insertTemplateAtLane(overlay, sample_template, lane_index)

    # Blending layers:
    output_img = blend(ground_texture, overlay)

    # Rotating image:
    r_x, r_y, r_z = img.getRotation(MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z)
    output_img = rotate(output_img, r_x, r_y, r_z, 0, 0, 0) # Must change later
    output_img, y_offset = bring_to_bottom(output_img)
    x_offset = 0 # Must change later

    # Getting the template location
    tracker = MarkTracker(DESTINY)
    tracker.addLocation(template_location, template_class)
    tracker.update(x_offset, y_offset, r_x)

    # Final blending:
    output_img = blend(bg_img, output_img)

    # Drawing bounding box around the template:
    draw_bbox(output_img, tracker.getLocation(0), RED) # Must change later

    # Saving image:
    save_image(output_img, path=DESTINY)

if __name__ == "__main__":
    main()