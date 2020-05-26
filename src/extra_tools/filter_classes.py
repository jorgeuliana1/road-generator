import json, sys, os, argparse

def import_annotations(annotations_path):
    # Opening file
    with open(annotations_path, "r") as f:
        lines = f.read().strip().split("\n")

    annotations = []
    for line in lines:
        info = line.split(",")
        annotations.append({
                "path" : info[0],
                "x0" : info[1],
                "y0" : info[2],
                "x1" : info[3],
                "y1" : info[4],
                "category" : info[5]
        })

    return annotations

def import_classes(classes_path, classes_to_keep):

    # Opening file
    with open(classes_path, "r") as f:
            classes_json = json.load(f)
    
    classes_list = list(classes_json.keys())

    # Returns only classes that will be kept
    return [ c for c in classes_list if c in classes_to_keep ]

def annotation_to_line(annotation):
    return "{},{},{},{},{},{}".format(annotation["path"],
            annotation["x0"], annotation["y0"],
            annotation["x1"], annotation["y1"],
            annotation["category"])

def substitute_in_annotation(annotations, class_to_substitute, new_class):
    for annotation in annotations:
        if annotation["category"] == class_to_substitute:
            annotation["category"] = new_class

def keep_in_annotation(annotations, allowed_classes):
    new_annotations = [ a for a in annotations if a["category"] in allowed_classes]
    return new_annotations

def arguments():

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--output')
    argparser.add_argument('--annotations')
    argparser.add_argument('--keep', nargs='+')
    argparser.add_argument('--swap', nargs='+')
    argparser.add_argument('--classes')
    values = vars(argparser.parse_args())

    return {
            "output_folder" : values['output'],
            "classes_path" : values['classes'],
            "annotations_path": values['annotations'],
            "keep" : values['keep'],
            #"substitute_from" : values['swap'][0],
            #"substitute_to" : values['swap'][1]
            }

def dump(annotations, classes, output_dir):
    
    # Creating the output folder:
    os.makedirs(output_dir, exist_ok=True)
    
    annotations_path = os.path.join(output_dir, "annotations.csv")
    classes_path = os.path.join(output_dir, "classes.json")
    
    # Dumping annotations.csv:
    with open(annotations_path, "w") as f:
        for annotation in annotations:
            f.write(annotation_to_line(annotation))
            if annotation != annotations[-1]: f.write("\n")

    # Dumping classes.json:
    classes_dict = {}
    for i in range(len(classes)):
        classes_dict[classes[i]] = i
    with open(classes_path, "w") as classes_json:
        classes_json.write(json.dumps(classes_dict, indent=2))

args = arguments()
annotations = import_annotations(args["annotations_path"])
classes = import_classes(args["classes_path"], args["keep"])

#substitute_in_annotation(annotations, args["substitute_from"], args["substitute_to"])
annotations = keep_in_annotation(annotations, args["keep"])

dump(annotations, classes, args["output_folder"])
