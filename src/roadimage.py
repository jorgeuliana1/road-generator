from road import Road
from mark_tracker import MarkTracker
import random
import math

class RoadImage:
    # Main informations:
    # - Image dimensions
    # - Image path
    # - Number of lanes

    # TODO: FINISH THE CLASS
    
    def __init__(self, dimensions, path, background_images, asphalt_textures, templates):
        self.w, self.h = dimensions
        self.templates = templates
        self.path = path
        self.road = Road(self.w, self.h)

        # Default values that can be changed later:
        self.seed = 0

    def setSeed(self, seed):
        self.seed = seed
        random.seed(self.seed)

    def defineLanes(self, number_of_lanes, variation):
        default_lane_proportion = (self.w / float(number_of_lanes))/float(self.w)
        
        # Variation is given in percentage

        # Creating the lanes:
        lane_sizes = []
        for i in range(number_of_lanes - 1):
            # "addition" is the variation in the specific lane
            addition = random.randint(-variation, variation) / 100.00 * default_lane_proportion
            lane_width = addition + default_lane_proportion
            lane_width = round(lane_width, 2) # Rounding the value to simplificate the sizes
            # Adding the lane sizes in a list to create the last lane without any size issue:
            lane_sizes.append(lane_width)
            self.road.newLane(math.ceil(lane_width*self.w))
        
        # Creating the last lane
        lanes_size = 0
        for i in lane_sizes:
            lanes_size += i
        lane_width = 1 - lanes_size
        self.road.newLane(math.floor(lane_width*self.w))

    def getRoad(self):
        return self.road