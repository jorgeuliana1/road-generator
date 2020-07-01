import cv2, math, json, os, sys, random
import numpy as np
from mark_tracker import MarkTracker
from road import Road
from roadimage import RoadImage
from roadgraphics import *
import random
from joblib import Parallel, delayed
import drawings as drw

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

def fill_csv_alternate(imagepath, templates, folder, filename):
    csv_path = os.path.join(folder, filename)
    with open(csv_path, "a+") as f:
        for template in templates:
            x0, y0, x1, y1 = map(lambda i : max(0, i), template.bounding_box)
            label = template.label
            _, imagename = os.path.split(imagepath)
            csv_line = f"images/{imagename},{x0},{y0},{x1},{y1},{label}\n"
            f.write(csv_line)

def save_classes(templates, filename, folder):
    t_labels = list(templates.labels)
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

def generate_image(json_file, i, templates_collection, ground_textures, backgrounds, NUMI):
    
    # Getting the parameters from the JSON file:
    image_info = json_file["image"]
    dataset_info = json_file["dataset"]
    road_info = json_file["road"]
    templates_info = json_file["templates"]
    elements_paths = dataset_info["elements_paths"]
    image_rotation = image_info["rotation"]
    roadlines_info = road_info["lines"]
    fx_info = image_info["effects"]
    WIDTH, HEIGHT = image_info["width"],  image_info["height"]
    MIN_LANES, MAX_LANES = road_info["lanes"]["amount"]
    LANE_VARIATION = road_info["lanes"]["width_variation"]
    MIN_X, MAX_X = image_rotation["x"]
    MIN_Y, MAX_Y = image_rotation["y"]
    MIN_Z, MAX_Z = image_rotation["z"]
    TR_MINH, TR_MAXH = templates_info["proportion"]
    TR_MINW, TR_MAXW = templates_info["proportion"]
    GROUND_TEXTURES = elements_paths["ground_textures"]
    BACKGROUNDS = elements_paths["backgrounds"]
    DES_FOLDER = dataset_info["title"]
    FN_PATTERN, F_EXTENSION = dataset_info["filename_pattern"].split("{}")
    MINCX, MAXCX = templates_info["delta_x"]
    MINCY, MAXCY = templates_info["delta_y"]
    MINS_WID, MAXS_WID = roadlines_info["width"]
    MIND_SIZ, MAXD_SIZ = roadlines_info["section_size"]
    MIND_DIS, MAXD_DIS = roadlines_info["section_distance"]
    MIN_XDIS, MAX_XDIS = roadlines_info["sublines_distance"]
    SEED = json_file["processing"]["seed"]
    _, MAXBLUR = fx_info["blur"]
    _, MAXCONTRAST = fx_info["contrast"]
    _, MAXBRIGHT = fx_info["brightness"]
    _, MAXAGE = fx_info["aging"]

    # Generating the templates layer:
    overlay = generate_empty_templates_layer((WIDTH, HEIGHT))

    # Creating the image
    images_counter = i
    DESTINY = generate_outpath(DES_FOLDER, FN_PATTERN, images_counter, F_EXTENSION, NUMI)
    if i == 0:
        set_seed = True
    else:
        set_seed = False
    img = RoadImage((WIDTH, HEIGHT), "", backgrounds, ground_textures, templates_collection, set_seed=set_seed)
    if i == 0:
        img.setSeed(SEED)

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
    x_offset, y_offset = img.getShift(MINCX, MAXCX, MINCY, MAXCY)
    templates_objs = img.insert_templates_at_lanes(x_offset, y_offset, TR_MINH, TR_MAXH, TR_MINW, TR_MAXW)

    # Rotating image:
    r_x, r_y, r_z = img.getRotation(MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z)
    
    TM = get_transformation_matrix((HEIGHT, WIDTH), r_x, r_y, r_z, 0, 0, 0)
    overlay = rotate(overlay, TM)
    ground_texture = rotate(ground_texture, TM)
    

    # Bringing to the bottom:
    ground_texture, y_shift = bring_to_bottom(ground_texture)
    overlay, y_shift = bring_to_bottom(overlay)
    x_shift = 0

    # Rotating templates:
    for i in range(len(templates_objs)):
        templates_objs[i] = templates_objs[i].apply_perspective(TM)
        dx, dy = templates_objs[i].displacement
        dx, dy = dx + x_shift, dy + y_shift
        templates_objs[i].displacement = dx, dy

    # Drawing the images into the overlay:
    overlay = img.draw_templates(overlay, templates_objs)
    
    # Aging roadmarks:
    age_matrix = img.getAgingMatrix(MAXAGE)
    overlay = age_layer(overlay, age_matrix)
    overlay = blur_borders(overlay)

    # Blending layers:
    output_img = blend(ground_texture, overlay)

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
    fill_csv_alternate(DESTINY, templates_objs, DES_FOLDER, "annotations.csv")

def main():

    # For information:
    print("Preparing to generate dataset...")

    # Getting settings JSON file's path:
    settings_path = sys.argv[1] # First argument on command-line

    # Opening the JSON file:
    with open(settings_path, 'r') as f:
        json_file = json.load(f)

    # Getting the parameters from the JSON file:
    dataset_info = json_file["dataset"]
    GROUND_TEXTURES = dataset_info["elements_paths"]["ground_textures"]
    BACKGROUNDS = dataset_info["elements_paths"]["backgrounds"]
    DES_FOLDER = dataset_info["title"]
    NUMI = dataset_info["length"]
    JOBS = json_file["processing"]["jobs"]

    # Loading the roadmarks templates:
    arrows_collection = drw.ArrowCollection(dataset_info["elements_paths"]["models"])

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
    Parallel(n_jobs=JOBS)(delayed(generate_image)(json_file, i, arrows_collection, ground_textures, backgrounds, NUMI) for i in range(NUMI))
    
    save_classes(arrows_collection, "classes.json", DES_FOLDER)
    print("Dataset generated successfully.")

if __name__ == "__main__":
    main()
