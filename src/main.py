import cv2, math, json, os, sys, random
import numpy as np
from mark_tracker import MarkTracker
from road import Road
from roadimage import RoadImage
from roadgraphics import *
import random
from joblib import Parallel, delayed

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(image, title="", path="image.jpg"):
    cv2.imwrite(title+path, image)

def fill_csv(trackers, title, path):
    with open(path+"/"+title, "a+") as f:
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

def list_images(path):
    files = os.listdir(path)
    return files.copy()

def generate_outpath(folder_path, name_pattern, image_count, file_extension, max_number):
    
    # Creating images_path (if it doesn't exist):
    images_path = os.path.join(folder_path, "images")
    os.makedirs(images_path, exist_ok=True)
    
    # Generating image number:
    max_number_decimals = len(str(max_number))
    count_str = list(str(image_count))
    while len(count_str) < max_number_decimals:
        count_str.insert(0, '0')
    count_str = "".join(count_str)

    # Returning the path:
    return folder_path + "/images/" + name_pattern + count_str + file_extension

def generate_image(json_file, i, templates, ground_textures, backgrounds, NUMI):
    
    # Getting the parameters from the JSON file:
    WIDTH = json_file["IMAGE_DIMENSIONS"]["WIDTH"]
    HEIGHT = json_file["IMAGE_DIMENSIONS"]["HEIGHT"]
    MAX_LANES = json_file["ROAD_SETTINGS"]["DIVISIONS"]["MAX"]
    MIN_LANES = json_file["ROAD_SETTINGS"]["DIVISIONS"]["MIN"]
    #LINE_THICKNESS = json_file["ROAD_SETTINGS"]["LINE_THICKNESS"]
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
    MAXBLUR = json_file["IMAGE_TRANSFORM"]["MAX_BLUR"]
    MAXCONTRAST = json_file["IMAGE_TRANSFORM"]["MAX_CONTRAST"]
    MAXBRIGHT = json_file["IMAGE_TRANSFORM"]["MAX_BRIGHTNESS"]
    MAXAGE = json_file["IMAGE_TRANSFORM"]["MAX_AGING"]


    # Generating the templates layer:
    overlay = generate_empty_templates_layer((WIDTH, HEIGHT))

    # Creating the image
    images_counter = i
    DESTINY = generate_outpath(DES_FOLDER, FN_PATTERN, images_counter, F_EXTENSION, NUMI)
    if i == 0:
        set_seed = True
    else:
        set_seed = False
    img = RoadImage((WIDTH, HEIGHT), "", backgrounds, ground_textures, templates, set_seed=set_seed)
    if i == 0:
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
    bg_img = load_image((WIDTH, HEIGHT), BACKGROUNDS + "/" + background_filename)

    # Getting random ground texture:
    ground_texture_filename = img.randomGround()
    ground_texture = load_image((WIDTH, HEIGHT), GROUND_TEXTURES + "/" + ground_texture_filename)
    
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

        tracker = MarkTracker(filename, (HEIGHT, WIDTH))
        tracker.addLocation((x0, y0, x1, y1), label)
        sub_trackers.append(tracker)

    # Aging roadmarks:
    age_matrix = img.getAgingMatrix(MAXAGE)
    overlay = age_layer(overlay, age_matrix)

    # Rotating image:
    r_x, r_y, r_z = img.getRotation(MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z)
    TM = get_transformation_matrix((HEIGHT, WIDTH), r_x, r_y, r_z, 0, 0, 0)
    overlay = rotate(overlay, TM)
    ground_texture = rotate(ground_texture, TM)

    # "Eroding" overlay borders:
    overlay = blur_borders(overlay)

    # Blending layers:
    output_img = blend(ground_texture, overlay)
    output_img, y_shift = bring_to_bottom(output_img)
    x_shift = 0

    # Updating marktrackers:
    for t in sub_trackers:
        t.applyPerspective(TM, (HEIGHT, WIDTH)) # Must change later
        t.move(x_shift, y_shift)

    # Final blending:
    output_img = blend(bg_img, output_img)

    # Applying the color distortions
    blur, contrast, brightness = img.getTransform(MAXBLUR, MAXCONTRAST, MAXBRIGHT)
    output_img = apply_color_distortions(output_img, brightness, contrast)
    output_img = apply_blur(output_img, blur)

    # Saving image:
    save_image(output_img, path=DESTINY)
    print("Generated image", images_counter+1, "of", NUMI)

    # Preparing for the next round:
    images_counter+=1

    # Saving trackers csv:
    fill_csv(sub_trackers, "annotations.csv", DES_FOLDER)

def main():

    # For information:
    print("Preparing to generate dataset...")

    # Getting settings JSON file's path:
    settings_path = sys.argv[1] # First argument on command-line

    # Opening the JSON file:
    with open(settings_path, 'r') as f:
        json_file = json.load(f)

    # Getting the parameters from the JSON file:
    WIDTH = json_file["IMAGE_DIMENSIONS"]["WIDTH"]
    HEIGHT = json_file["IMAGE_DIMENSIONS"]["HEIGHT"]
    PATHS = json_file["PATHS"]
    GROUND_TEXTURES = PATHS["GROUND_TEXTURES"]
    TEMPLATES = PATHS["TEMPLATES"]
    BACKGROUNDS = PATHS["BACKGROUND_IMAGES"]
    DES_FOLDER = PATHS["DESTINY_FOLDER"]
    NUMI = json_file["IMAGES"]
    JOBS = json_file["JOBS"]

    images_counter = 0 # To generate filename

    # Loading the roadmarks templates:
    templates = load_templates(TEMPLATES, (WIDTH, HEIGHT))

    # Loading ground textures:
    ground_textures = list_images(GROUND_TEXTURES)

    # Loading the backgrounds:
    backgrounds = list_images(BACKGROUNDS)

    # Creating the output directory (if it doesn't exist):
    os.makedirs(DES_FOLDER, exist_ok=True)
    
    # Deleting csv file (if it exists):
    csv_filename = "annotations.csv" 
    dest_folder  = os.listdir(DES_FOLDER)
    if csv_filename in dest_folder:
        csv_filepath = os.path.join(DES_FOLDER, csv_filename)
        os.remove(csv_filepath)

    # Multicore processing:
    Parallel(n_jobs=JOBS)(delayed(generate_image)(json_file, i, templates, ground_textures, backgrounds, NUMI) for i in range(NUMI))
    
    save_classes(templates, "classes.json", DES_FOLDER)
    print("Dataset generated successfully.")

if __name__ == "__main__":
    main()
