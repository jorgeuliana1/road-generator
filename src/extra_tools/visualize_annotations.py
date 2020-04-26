import cv2, os, sys
import numpy as np

# This script allow us to visualize the annotations of a generated dataset.

def get_arguments():

    # Returns a dictionary containing arguments from the command-line

    return {
        "dataset_root" : sys.argv[1],
        "output_directory" : sys.argv[2]
    }

def get_annotations(annotations_csv_path):

    # Returns a list of dictionaries
    # Each dictionary of the list is an annotated image

    images_dict = {} # We use a dict to merge the annotations by image
    
    # Opening the csv file:
    with open(annotations_csv_path, "r") as annotations_file:
        annotation_lines = annotations_file.read().strip().split("\n")

    # Inserting each annotation to the images_dict
    for line in annotation_lines:

        # Getting annotation info:
        annotation_info = line.split(",")
        image_rel_path = annotation_info[0] # Image relative path
        x0, y0 = annotation_info[1], annotation_info[2]
        x1, y1 = annotation_info[3], annotation_info[4]
        category = annotation_info[5]

        annotation_dict = {
            "x0" : int(x0),
            "y0" : int(y0),
            "x1" : int(x1),
            "y1" : int(y1),
            "category" : category
        }

        # Inserting the annotation at the images_dict:
        if image_rel_path in images_dict.keys():
            images_dict[image_rel_path]["annotations"].append(annotation_dict)
        else:
            images_dict[image_rel_path] = {
                "image_name" : image_rel_path,
                "annotations" : [annotation_dict]
            }

    # Converting from images_dict to images_list:
    images_list = []
    for key in images_dict.keys():
        images_list.append(images_dict[key])

    return images_list

def draw_bounding_box(image, x0, y0, x1, y1, color=(0, 0, 255), thickness=3):

    return cv2.rectangle(image, (x0, y0), (x1, y1), color, thickness)

def main():

    # Getting arguments:
    args = get_arguments()

    # Opening the input file:
    input_dir = args["dataset_root"]
    annotations_csv_path = os.path.join(input_dir, "annotations.csv")
    images = get_annotations(annotations_csv_path)

    # Creating the output directory (if it doesn't exist):
    output_dir = args["output_directory"]
    images_dir = os.path.join(output_dir)
    os.makedirs(os.path.join(images_dir, "images"), exist_ok=True)

    for i in images:

        # Reading the image
        input_image_path = os.path.join(input_dir, i["image_name"])
        out_image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)

        # Drawing every bounding box of the image in the output image
        for annotation in i["annotations"]:

            x0, y0 = annotation["x0"], annotation["y0"]
            x1, y1 = annotation["x1"], annotation["y1"]

            out_image = draw_bounding_box(out_image, x0, y0, x1, y1)

        # Saving the output image
        output_path = os.path.join(images_dir, i["image_name"])
        cv2.imwrite(output_path, out_image)

    return

if __name__ == "__main__":
    main()