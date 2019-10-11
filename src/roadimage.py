from road import Road
from mark_tracker import MarkTracker
from roadgraphics import *
import random
import math

class RoadImage:
    def __init__(self, dimensions, path, background_images, asphalt_textures, templates, seed=0):
        self.w, self.h = dimensions
        self.path = path # Where the image will be saved
        self.road = Road(self.w, self.h)

        # Defining the dictionaries containing random images
        self.templates = templates
        self.backgrounds = background_images
        self.grounds = asphalt_textures

        random.seed(seed)

    def setSeed(self, seed):
        random.seed(seed)

    def defineLanes(self, min_lanes, max_lanes, variation):

        number_of_lanes = random.randint(min_lanes, max_lanes)
        self.number_of_lanes = number_of_lanes

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
        lane_width = self.w - math.floor(lanes_size * self.w)
        self.road.newLane(lane_width)

    def getRoad(self):
        return self.road
    
    def randomMark(self): # Returns a random template name
        templates_names = tuple(self.templates.keys())
        random_key = templates_names[random.randint(0,len(templates_names) - 1)]
        return random_key

    def randomBackground(self): # Returns a random background name
        background_names = tuple(self.backgrounds.keys())
        random_key = background_names[random.randint(0,len(background_names) - 1)]
        return random_key

    def randomGround(self):
        ground_names = tuple(self.grounds.keys())
        random_key = ground_names[random.randint(0,len(ground_names) - 1)]
        return random_key

    def getRotation(self, minx, maxx, miny, maxy, minz, maxz):

        # Getting rotations, in deegrees
        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)
        z = random.randint(minz, maxz)

        # Converting to radians:
        x = x/180.00 * math.pi
        y = y/180.00 * math.pi
        z = z/180.00 * math.pi

        # Returning rotations:
        return (x, y, z)
    
    def getShift(self, minx, maxx, miny, maxy):
        # Getting shifts, in pixels
        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)

        return (x, y)        

    def getRandomLane(self):
        lanes = len(self.road.lanes)
        return random.randint(0, lanes-1)

    def getRandomSeparator(self, minwidth, maxwidth, mindotsize, maxdotsize, mindotdist, maxdotdist, minxdist, maxxdist):

        # Defining colors:
        colors = [
                    (255, 255, 255), # WHITE
                    (255, 255,   0), # YELLOW
                    (128, 128,   0)  # DARK YELLOW
                 ]
        
        # Getting random color:
        color = colors[random.randint(0,len(colors)-1)]

        # Getting random dot_size:
        dot_size = random.randint(mindotsize, maxdotsize)

        # Getting random dot_dist:
        dot_dist = random.randint(mindotdist, maxdotdist)

        # Getting random x_dist:
        x_dist = random.randint(minxdist, maxxdist)

        # Getting random width:
        width = random.randint(minwidth, maxwidth)

        # Getting random true or false:
        is_true = bool(random.getrandbits(1))

        return (width, color, is_true, dot_size, dot_dist, x_dist)

    def getLanesNumber(self):
        return self.number_of_lanes

    def insertTemplatesAtLanes(self, layer, x=0, y=0, max_h=100, min_h=100, max_w=100, min_w=100):
        # Creating insertion lists:
        lanes = []
        templates = []

        # Selecting the number of lanes that will not be empty:
        n_lanes = random.randint(-self.number_of_lanes, self.number_of_lanes)
        n_lanes = abs(n_lanes) # This makes it harder to have 0 lanes

        # Selecting the lanes that will be filled and the content:
        for i in range(n_lanes):
            j = self.getRandomLane()
            while j in set(lanes):
                j = self.getRandomLane()
                continue
            lanes.append(j)
            templates.append(random.randint(0, len(self.templates)))

        # Filling lanes
        locations = []
        for i in range(len(lanes)):
            road = self.getRoad()
            template_names = tuple(self.templates.keys())

            # Setting up template:
            template = self.templates[template_names[templates[i] - 1]].copy()
            h, w, _ = template.shape
            dh, dw = int(random.randint(min_h, max_h) / 100 * h), int(random.randint(min_w, max_w) / 100 * w)
            template = resize_template(template, dh, dw)

            layer, location = road.insertTemplateAtLane(layer, template, lanes[i], x=x, y=y)
            locations.append((location, template_names[templates[i] - 1]))
        
        return layer, locations

    def getTransform(self, maxblur, maxconstrast, maxbrightness):
        constrast = random.randint(0, maxconstrast)
        brightness = random.randint(0, maxbrightness)
        blurvalues = [1, 1, 3, 3, 5, 5, 7, 7, 9, 9]
        constrast = random.randint(0, maxconstrast)
        blur = blurvalues[random.randint(0, maxblur)]

        return blur, constrast/100, brightness/100

    def getAgingMatrix(self):

        def getAge(limiter):
            age = random.randint(-limiter, limiter)
            if age < 0:
                age = 0
            elif age > 100:
                age = 100

            return age

        h, w = self.h, self.w
        mw = math.floor(math.sqrt(h))
        mh = mw

        matrix = []

        for i in range(0, mh):
            matrix.append([])
            for j in range(0, mw):
                new = 100 - getAge(50) # How "new/fresh" the finish is
                matrix[i].append(new)

        return matrix