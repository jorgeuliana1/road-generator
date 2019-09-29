import math

class MarkTracker:
    filename = ""
    locations = []

    def __init__(self, filename):
        self.filename = filename
    def addLocation(self, location, m_class):
        track = (location, m_class)
        self.locations.append(track)
    def getLocationString(self, index):
        location = self.locations[index]
        location, _ = location

        # Getting Xs and Ys:
        pos0, pos1 = location
        x0, y0 = pos0
        x1, y1 = pos1

        string = str(x0) + "," + str(y0) + "," + str(x1) + "," + str(y1)
        return string
    def getClass(self, index):
        location   = self.locations[index]
        _, m_class = location

        return m_class
    def getInformation(self, index):
        return getLocationString(self, index) + "," + getClass(self, index)
    def location_after_moving(location, x_movement, y_movement):
        pos0, pos1 = location
        x0, y0 = pos0
        x1, y1 = pos1

        return ((x0 + x_movement, y0 + y_movement), (x1 + x_movement, y1 + y_movement))
    def location_after_perspective(location, rotation_radians):
        # Getting Xs and Ys:
        pos0, pos1 = location
        x0, y0 = pos0
        x1, y1 = pos1

        # Putting points in cartesian coordinates
        ref_x = (x0 + x1) / 2
        ref_y = (y0 + y1) / 2
        x0, x1 = x0 - ref_x, x1 - ref_x
        y0, y1 = y0 - ref_y, y1 - ref_y

        # Converting to 3D points
        # pos0 = (x0, y0, 0)
        # pos1 = (x1, y1, 0)
        # The rotation must follow the rule:
        # z ** 2 + y ** 2 = y0 ** 2
        # Thus:
        # z = y0*cos(radians)
        # y = y0*sin(radians)

        # Doing the rotation:
        pos0 = (x0, y0*math.cos(rotation_radians), y0*math.sin(rotation_radians))
        pos1 = (x1, y1*math.cos(rotation_radians), y1*math.sin(rotation_radians))

        # Converting to 2D:
        x0, y0, _ = pos0
        x1, y1, _ = pos1
        x0, y0 = x0 * 2.4 + ref_x, y0 * 1.2 + ref_y # Returning to default coordinates
        x1, y1 = x1 * 2.4 + ref_x, y1 * 1.2 + ref_y # Returning to default coordinates
        pos0 = (int(x0), int(y0))
        pos1 = (int(x1), int(y1))

        new_location = (pos0, pos1)

        return new_location
    def updateLocation(self, index, x_move, y_move, x_rotation):
        location = self.locations[index]
        pos, m_class = location
        pos = MarkTracker.location_after_perspective(pos, x_rotation)
        pos = MarkTracker.location_after_moving(pos, x_move, y_move)
        location = (pos, m_class)
        self.locations[index] = location
    def update(self, x_move, y_move, x_rotation):
        for i in range(len(self.locations)):
            self.updateLocation(i, x_move, y_move, x_rotation)
    def getLocation(self, index):
        loc = self.locations[index]
        pos, _ = loc
        loc0, loc1 = pos
        x0, y0 = loc0
        x1, y1 = loc1
        return ((int(x0), int(y0)), (int(x1), int(y1)))
    def getFilename(self):
        return self.filename
