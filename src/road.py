from lane import Lane

class Road:
    h, w = 0, 0
    lanes = []

    def __init__(self, w, h):
        self.w = w # Road width
        self.h = h # Road height
    def newLane(self, lane_width):
        # Getting informations of the last created lane, if it exists
        lane_x0 = 0 # Default value
        if len(lanes) > 0:
            last_lane = self.lanes[-1]
            lane_x0 = last_lane.x0 + last_lane.w

        # Invalid lane size
        if lane_x0 > self.w:
            return
        
        new_lane = Lane(lane_x0, lane_width, self.h)
        lanes.append(new_lane)
    def insertTemplateAtLane(self, layer, template, lane_index, x=0, y=0):
        lane = self.lanes[lane_index]
        return lane.insertTemplate(layer, template, x, y)
