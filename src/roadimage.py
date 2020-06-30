from road import Road
from mark_tracker import MarkTracker
from roadgraphics import *
from crosswalk import CrossWalk
import random
import math
import drawings as drw

class RoadImage:
    def __init__(self, dimensions, path, background_images, asphalt_textures, templates_collection, seed=0, set_seed=True):
        self.w, self.h = dimensions
        self.path = path # Where the image will be saved
        self.road = Road(self.w, self.h)

        # Defining the dictionaries containing random images
        self.templates_collection = templates_collection
        self.backgrounds = background_images
        self.grounds = asphalt_textures

        if set_seed:
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
        backgrounds = self.backgrounds
        return backgrounds[random.randint(0, len(backgrounds) - 1)]

    def randomGround(self):
        grounds = self.grounds
        return grounds[random.randint(0, len(grounds) - 1)]

    def getRotation(self, minx, maxx, miny, maxy, minz, maxz):

        def randomRotation(mind, maxd):
            multiplier = random.randint(0, 1000) / 1000
            difference = maxd - mind
            
            return multiplier * difference + mind

	# Getting Y and Z rotation signals (positive or negative):
        ysig = random.sample((-1, 1), 1)[0]
        zsig = random.sample((-1, 1), 1)[0]

        # Getting rotations, in deegrees
        x = -randomRotation(minx, maxx)
        y = ysig * randomRotation(miny, maxy)
        z = zsig * randomRotation(minz, maxz)

        # Converting to radians:
        x = x/180.00 * math.pi
        y = y/180.00 * math.pi
        z = z/180.00 * math.pi

        # Returning rotations:
        return (x, y, z)
    
    def getShift(self, minx, maxx, miny, maxy):
        # Getting shifts, in pixels
        x = random.randint(0, 100) / 100 * (maxx - minx) + minx
        y = random.randint(0, 100) / 100 * (maxy - miny) + miny

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

    def insert_templates_at_lanes(self, delta_x, delta_y, min_h, max_h, min_w, max_w):
        """
        min_h, max_h, min_w and max_w are proportions, they must be between 0 and 1
        delta_x and delta_y are proportions, they must be between 0 and 1
        """
        labels = self.templates_collection.labels
        m = len(labels) # m : number of loaded templates.
        road = self.getRoad()
        # L is a vector which each index represents a lane in the road:
        L = [math.ceil(m * random.randint(0, 100) / 100) for i in range(self.number_of_lanes)]
        # Creating one empty lane:
        if len(L) > 1:
            L[int(random.randint(0, 100) / 100) * (len(L)) - 1] = -1 # -1 means that there will be no template at that lane.
        # Defining the exact position and vectors of the to-be-inserted templates:
        templates = []
        for l in range(len(L)):
            Ln = L[l] - 1
            if Ln == -1: continue # Skipping the "supposed-to-be-empty" lanes
            lane = road.lanes[l]
            # Defining the template's dimensions:
            min_size = (min_h + min_w) / 2 * lane.w
            max_size = (max_h + max_w) / 2 * lane.w
            base_siz = random.randint(0, 100) / 100 * (max_size - min_size) + min_size
            base_dim = (int(base_siz), int(base_siz))
            # Getting the template vector:
            template = self.templates_collection.get(labels[Ln], base_dim)
            # Inserting the template at the lane:
            dx, dy = lane.getAbsoluteCoordinates(int(delta_x * lane.w), int(delta_y * lane.h))
            template.displacement = dx, dy
            templates.append(template)
        return templates

    def draw_templates(self, img, templates):
        for template in templates:
            img = template.draw(img, (255, 255, 255, 255))
        return img

    def getTransform(self, maxblur, maxconstrast, maxbrightness):
        constrast = random.randint(0, maxconstrast)
        brightness = random.randint(0, maxbrightness)
        blurvalues = [1, 1, 3, 3, 5, 5, 7, 7, 9, 9]
        constrast = random.randint(0, maxconstrast)
        blur = blurvalues[random.randint(0, maxblur)]

        return blur, constrast/100, brightness/100

    def getAgingMatrix(self, max_age):

        h, w = self.h, self.w
        aging_matrix = np.abs(np.random.randn(h, w))
        aging_matrix = np.clip(aging_matrix, 0, 0.01 * max_age)

        return aging_matrix
