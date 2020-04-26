import json, sys, os

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

def import_classes(classes_path):
    # Opening file
    with open(classes_path, "r") as f:
            classes_json = json.load(f)
    
    classes_list = list(classes_json.keys())

    # Filtering the classes list:
    if "__background__" in classes_list:
        classes_list.remove("__background__")

    return classes_list

def annotation_to_line(annotation):
    return "{},{},{},{},{},{}".format(annotation["path"],
            annotation["x0"], annotation["x1"],
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
    args = sys.argv
    
    def get_tag_contents(args, tag):

        for i in range(len(args)):
            if args[i] == "--{}".format(tag):
                break

        def is_tag(string):
            return "--" in string

        j = i + 1
        for j in range(i + 1, len(args)):
            if is_tag(args[j]):
                break

        return tuple(args[i + 1:j])

    output = get_tag_contents(args, "output")
    classes = get_tag_contents(args, "classes")
    annotations = get_tag_contents(args, "annotations")
    keep = get_tag_contents(args, "keep")
    substitute = get_tag_contents(args, "swap")

    if len(substitute) % 2 != 0:
        quit()

    return {
            "output_folder" : output,
            "classes_path" : classes,
            "annotations_path": annotations,
            "keep" : keep,
            "substitute_from" : substitute[0],
            "substitute_to" : substitute[1]
            }

def dump(annotations, classes, output_dir):
    
    # Creating the output folder:
    os.makedirs(output_dir, exist_ok=True)
    
    annotations_path = os.path.join(output_dir, "annotations.csv")
    classes_path = os.path.join(output_dir, "classes.json")
    
    with open(annotations_path, "w") as f:
        for annotation in annotations:
            f.write(annotation_to_line(annotation))
            if annotation != annotations[-1]: f.write("\n")

args = arguments()
annotations = import_annotations(args["annotations_path"][0])
classes = import_classes(args["classes_path"][0])

substitute_in_annotation(annotations, args["substitute_from"], args["substitute_to"])
annotations = keep_in_annotation(annotations, args["keep"])

dump(annotations, classes, args["output_folder"][0])

print(args)
