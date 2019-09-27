from lane import Lane

class Road:
    def __init__(self, w, h):
        self.w = w # Road width
        self.h = h # Road height
        self.lanes = [] # List of lanes
    def newLane(self, lane_width):
        # Getting informations of the last created lane, if it exists
        lane_x0 = 0 # Default value
        if len(self.lanes) > 0:
            last_lane = self.lanes[-1]
            lane_x0 = last_lane.x0 + last_lane.w

        # Invalid lane size
        if lane_x0 > self.w:
            return
        
        new_lane = Lane(lane_x0, lane_width, self.h)
        self.lanes.append(new_lane)
    def insertTemplateAtLane(self, layer, template, lane_index, x=0, y=0):
        lane = self.lanes[lane_index]
        
        # Defining if the number of lanes is even:
        even = False
        if len(self.lanes) % 2 == 0:
            even = True

        return lane.insertTemplate(layer, template, x, y, even=even)
    def drawSeparator(self, index, layer, width=3, color=(255, 255, 255), dotted=False, dot_size=3, dot_distance=1, x_dist=0):
        if len(self.lanes) <= index+1:
            return layer
        
        # Defining the lanes:
        lane1 = self.lanes[index]
        lane2 = self.lanes[index + 1]

        new_layer = layer.copy()

        # Drawing the lanes:
        new_layer = lane1.drawRightSeparator(new_layer, width=width, color=color, dotted=dotted, dot_size=dot_size, dot_distance=dot_distance, x_dist=x_dist)
        new_layer = lane2.drawLeftSeparator(new_layer, width=width, color=color, dotted=dotted, dot_size=dot_size, dot_distance=dot_distance, x_dist=x_dist)

        return new_layer