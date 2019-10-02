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

def load_backgrounds(path, dimensions):
    files = os.listdir(path)
    backgrounds = {}

    for filename in files:
        full_path = path + "/" + filename
        background_name = filename.split(".")[0]

        background = get_bg_from_image(dimensions, full_path)
        backgrounds[background_name] = background
    
    # Can be used for ground textures and backgrounds
    return backgrounds

def generate_outpath(folder_path, name_pattern, image_count, file_extension, max_number):

    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    if not os.path.isdir(folder_path+"/images"):
        os.mkdir(folder_path+"/images")
    
    # Generating image number:
    max_number_decimals = len(str(max_number))
    count_str = list(str(image_count))
    while len(count_str) < max_number_decimals:
        count_str.insert(0, '0')
    count_str = "".join(count_str)

    # Returning the path:
    return folder_path + "/images/" + name_pattern + count_str + file_extension

def main():

    # For information:
    print("Preparing to generate dataset...")

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
    GROUND_TEXTURES = PATHS["GROUND_TEXTURES"]
    TEMPLATES = PATHS["TEMPLATES"]
    BACKGROUNDS = PATHS["BACKGROUND_IMAGES"]
    DES_FOLDER = PATHS["DESTINY_FOLDER"]
    FN_PATTERN = PATHS["FILENAME_PATTERN"]
    F_EXTENSION = PATHS["FILENAME_EXTENSION"]

    POS = json_file["MARKPOS_VARIATION"]
    MINCX, MAXCX = POS["MIN_X"], POS["MAX_X"]
    MINCY, MAXCY = POS["MIN_Y"], POS["MAX_Y"]

    SEP = json_file["SEP_SETTINGS"]
    MINS_WID, MAXS_WID = SEP["MIN_WID"], SEP["MAX_WID"]
    MIND_SIZ, MAXD_SIZ = SEP["MIN_DOT_SIZ"], SEP["MAX_DOT_SIZ"]
    MIND_DIS, MAXD_DIS = SEP["MIN_DOT_DIS"], SEP["MAX_DOT_DIS"]
    MIN_XDIS, MAX_XDIS = SEP["MIN_XDIST"], SEP["MAX_XDIST"]

    SEED = json_file["SEED"]
    NUMI = json_file["IMAGES"]

    images_counter = 0 # To generate filename

    # Loading the roadmarks templates:
    templates = load_templates(TEMPLATES, (WIDTH, HEIGHT), ROAD_LANES)
    # Loading ground textures:
    ground_textures = load_backgrounds(GROUND_TEXTURES, (WIDTH, HEIGHT))
    # Loading the backgrounds:
    backgrounds = load_backgrounds(BACKGROUNDS, (WIDTH, HEIGHT))

    for i in range(NUMI):
        # Image generation loop

        # Generating the templates layer:
        overlay = generate_empty_templates_layer((WIDTH, HEIGHT))

        # Creating the image
        DESTINY = generate_outpath(DES_FOLDER, FN_PATTERN, images_counter, F_EXTENSION, NUMI)
        img = RoadImage((WIDTH, HEIGHT), DESTINY, backgrounds, ground_textures, templates)
        img.setSeed(SEED)

        # Defining the lanes in the road
        img.defineLanes(ROAD_LANES, LANE_VARIATION)

        # Defining the separators:
        separator_settings = img.getRandomSeparator(MINS_WID, MAXS_WID, MIND_SIZ, MAXD_SIZ,
                                                    MIND_SIZ, MAXD_SIZ, MIN_XDIS, MAX_XDIS)

        road = img.getRoad()
        # Inserting the lanes divisions in the road:
        for i in range(1, ROAD_LANES):
            if i > 0:
                overlay = road.drawSeparatorByTuple(i - 1, overlay, separator_settings)

        # Getting random background:
        background_filename = img.randomBackground()
        bg_img = backgrounds[background_filename]

        # Getting random ground texture:
        ground_texture_filename = img.randomGround()
        ground_texture = ground_textures[ground_texture_filename]
        
        # Inserting random template:
        template_class = img.randomMark()
        sample_template = templates[template_class]
        lane_index = img.getRandomLane()
        x_offset, y_offset = img.getShift(MINCX, MAXCX, MINCY, MAXCY)
        overlay, template_location = road.insertTemplateAtLane(overlay,
                                    sample_template, lane_index, x=x_offset, y=y_offset)

        # Blending layers:
        output_img = blend(ground_texture, overlay)

        # Rotating image:
        r_x, r_y, r_z = img.getRotation(MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z)
        output_img = rotate(output_img, r_x, r_y, r_z, 0, 0, 0) # Must change later
        output_img, y_shift = bring_to_bottom(output_img)
        x_shift = 0

        # Getting the template location
        tracker = MarkTracker(DESTINY)
        tracker.addLocation(template_location, template_class)
        tracker.update(x_shift, y_shift, r_x)

        # Final blending:
        output_img = blend(bg_img, output_img)

        # Drawing bounding box around the template:
        # draw_bbox(output_img, tracker.getLocation(0), RED) # Must change later

        # TODO: FIX THE TRACKER

        # Saving image:
        save_image(output_img, path=DESTINY)
        print("Generated image", images_counter+1, "of", NUMI)

        # Preparing for the next round:
        images_counter+=1
        SEED+=1 # Must find a better solution later, but for now it works well

    print("Dataset generated successfully.")

if __name__ == "__main__":
    main()