import cv2
import numpy as np
import math
import json
import os
from mark_tracker import MarkTracker
from road import Road
from roadimage import RoadImage
from roadgraphics import *
import random

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image, title="", path="image.jpg"):
    cv2.imwrite(title+path, image)

def save_csv(trackers, title, path):
    with open(path+"/"+title, 'w') as f:
        for t in trackers:
            f.write(t.getString()+"\n")

def save_classes(templates, filename, folder):
    t_labels = list(templates.keys())
    t_labels.insert(0, "__background__")

    with open(folder+"/"+filename, "w") as f:
        f.write("{\n")
        for i in range(0, len(t_labels)):
            f.write("\t\""+t_labels[i]+"\": "+str(i))
            if i != len(t_labels) - 1:
                f.write(",\n")
            else:
                f.write("\n")
        f.write("}")

def load_templates(path, dimensions):
    files = os.listdir(path)
    templates = {}

    for filename in files:
        full_path = path + "/" + filename
        template_name = filename.split(".")[0]

        template = get_template_from_image(dimensions, full_path)
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

    MAX_LANES = json_file["ROAD_SETTINGS"]["DIVISIONS"]["MAX"]
    MIN_LANES = json_file["ROAD_SETTINGS"]["DIVISIONS"]["MIN"]
    LINE_THICKNESS = json_file["ROAD_SETTINGS"]["LINE_THICKNESS"]
    LANE_VARIATION = json_file["ROAD_SETTINGS"]["VARIATION"]

    IMAGE_ROTATION = json_file["IMAGE_ROTATION"]
    MIN_X, MAX_X = IMAGE_ROTATION["MIN_X"], IMAGE_ROTATION["MAX_X"]
    MIN_Y, MAX_Y = IMAGE_ROTATION["MIN_Y"], IMAGE_ROTATION["MAX_Y"]
    MIN_Z, MAX_Z = IMAGE_ROTATION["MIN_Z"], IMAGE_ROTATION["MAX_Z"]

    TEMPLATE_RESIZE = json_file["TEMPLATE_RESIZE"]
    TR_MAXH = TEMPLATE_RESIZE["MAX_H"]
    TR_MINH = TEMPLATE_RESIZE["MIN_H"]
    TR_MAXW = TEMPLATE_RESIZE["MAX_W"]
    TR_MINW = TEMPLATE_RESIZE["MIN_W"]

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
    MAXBLUR = json_file["IMAGE_TRANSFORM"]["MAX_BLUR"]
    MAXCONTRAST = json_file["IMAGE_TRANSFORM"]["MAX_CONTRAST"]
    MAXBRIGHT = json_file["IMAGE_TRANSFORM"]["MAX_BRIGHTNESS"]

    images_counter = 0 # To generate filename

    # Loading the roadmarks templates:
    templates = load_templates(TEMPLATES, (WIDTH, HEIGHT))
    # Loading ground textures:
    ground_textures = load_backgrounds(GROUND_TEXTURES, (WIDTH, HEIGHT))
    # Loading the backgrounds:
    backgrounds = load_backgrounds(BACKGROUNDS, (WIDTH, HEIGHT))
    # Creating marktrackers list:
    trackers = []

    for i in range(NUMI):
        # Image generation loop

        # Generating the templates layer:
        overlay = generate_empty_templates_layer((WIDTH, HEIGHT))

        # Creating the image
        DESTINY = generate_outpath(DES_FOLDER, FN_PATTERN, images_counter, F_EXTENSION, NUMI)
        img = RoadImage((WIDTH, HEIGHT), DESTINY, backgrounds, ground_textures, templates)
        img.setSeed(SEED)

        # Creating the marktrackers sublist:
        sub_trackers = []

        # Defining the lanes in the road
        img.defineLanes(MIN_LANES, MAX_LANES, LANE_VARIATION)
        ROAD_LANES = img.getLanesNumber()

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
        overlay, template_locations = img.insertTemplatesAtLanes(overlay, x=x_offset, y=y_offset, min_w=TR_MINW, max_w=TR_MAXW, min_h=TR_MINH, max_h=TR_MAXH)

        # Creating marktrackers:
        for i in template_locations:
            p, label = i
            p1, p2 = p
            x0, y0 = p1
            x1, y1 = p2

            filename = "" + DESTINY
            filename = filename[len(DES_FOLDER)+1:]

            tracker = MarkTracker(filename)
            tracker.addLocation((x0, y0, x1, y1), label)
            sub_trackers.append(tracker)

        # Aging roadmarks:
        age_matrix = img.getAgingMatrix()
        overlay = age_layer(overlay, age_matrix)

        # Blending layers:
        output_img = blend(ground_texture, overlay)

        # Rotating image:
        r_x, r_y, r_z = img.getRotation(MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z)
        output_img = rotate(output_img, r_x, r_y, r_z, 0, 0, 0) # Must change later
        output_img, y_shift = bring_to_bottom(output_img)
        x_shift = 0

        # Updating marktrackers:
        for t in sub_trackers:
            t.applyPerspective(r_x, r_y, r_z, 0, 0, 0, (HEIGHT, WIDTH)) # Must change later
            t.move(x_shift, y_shift)

        # Final blending:
        output_img = blend(bg_img, output_img)

        # Applying the color distortions
        blur, contrast, brightness = img.getTransform(MAXBLUR, MAXCONTRAST, MAXBRIGHT)
        output_img = apply_color_distortions(output_img, brightness, contrast)
        output_img = apply_blur(output_img, blur)

        # Drawing bounding boxes around the templates (for testing purposes only):
        #for t in sub_trackers:
            #draw_bbox(output_img, t.getLocation(), RED)

        # Saving image:
        save_image(output_img, path=DESTINY)
        print("Generated image", images_counter+1, "of", NUMI)

        # Preparing for the next round:
        images_counter+=1
        SEED+=random.randint(0, 255) # Must find a better solution later, but for now it works well

        trackers += sub_trackers

    # Saving trackers csv:
    save_csv(trackers, "annotations.csv", DES_FOLDER)
    save_classes(templates, "classes.json", DES_FOLDER)

    print("Dataset generated successfully.")

if __name__ == "__main__":
    main()