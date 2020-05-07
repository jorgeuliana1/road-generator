import sys

def main():
    
    annotation_path = sys.argv[1]
    
    with open(annotation_path, "r") as annotation_file:
        csv_lines = annotation_file.read().strip().split("\n")
    
    categories_occurrences = {}
    for csv_line in csv_lines:

        csv_info = csv_line.split(",")
        _, _, _, _, _, category = csv_info

        if category not in categories_occurrences.keys():
            categories_occurrences[category] = 1
        else:
            categories_occurrences[category] += 1

    print(categories_occurrences)

if __name__ == "__main__":
    main()
