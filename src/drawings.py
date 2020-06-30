import numpy as np
import cv2 as cv
import json, os

class Arrow:
    """
    Private properties:
        arr_info : dictionary containing info about the arrow.
        base_dimensions : tuple containing the base dimensions of the arrow (w, h).
        arrow_vector : np.ndarray containing the points of the arrow polygon.

    Public properties:
        vector : reference to arrow_vector.
        label : reference to arr_info["label"]
        bounding_box : the bounding box of the arrow

    Note that every time we refer to arrow dimensions we are refering to values between 0 and 1.
    While when we refer to image dimensions we are refering to pixel values.
    """
    def __init__(self, arr_info, base_dimensions):
        # Defining the object properties:
        self.__arr_info = arr_info
        self.__base_dimensions = base_dimensions

        arrowhead_vector = self.__define_arrowhead()
        arrowbody_vector = self.__define_arrowbody()

        self.__arrow_vector = np.concatenate((arrowbody_vector, arrowhead_vector))

    def __define_arrowbody(self):
        """
        Returns a np.ndarray (a vector) of the points that contains the arrow body.
        """
        
        # If there is no body, we return a empty np.ndarray:
        if not self.__arr_info["has_body"]: return np.zeros((0, 2), np.int32)

        # Getting body information:
        body_info = self.__arr_info["body"]
        img_width, img_height = self.__base_dimensions
        body_width = body_info["width"]
        body_height = body_info["height"]

        # Defining the body vertices:
        y0 = (1 - body_height) * img_height
        y1 = img_height
        x0 = (0.5 - body_width / 2) * img_width
        x1 = (0.5 + body_width / 2) * img_width
        return np.array([[x0, y0], [x0, y1], [x1, y1], [x1, y0]], np.int32)

    def __define_arrowhead(self):
        """
        Returns a np.ndarray (a vector) of the points that contains the arrowhead.
        """

        # If there is no head, we return a empty np.ndarray:
        if not self.__arr_info["has_head"]: return np.zeros((0, 2), np.int32)

        # Getting head (and some body) information:
        head_info = self.__arr_info["head"]
        body_info = self.__arr_info["body"]
        img_width, img_height = self.__base_dimensions
        head_width = head_info["width"]
        head_height = head_info["height"]
        body_height = body_info["height"]

        # Notice that body_y0 == head_y1.
        # Defining the head vertices:
        y1 = (1 - body_height) * img_height
        y0 = y1 - head_height * img_height
        x0 = (0.5 - head_width / 2) * img_width
        x1 = (0.5 + head_width / 2) * img_width
        xc = (x0 + x1) / 2
        return np.array([[x1, y1], [xc, y0], [x0, y1]], np.int32)

    @property
    def vector(self):
        return self.__arrow_vector

    @property
    def label(self):
        return self.__arr_info["label"]

    @property
    def bounding_box(self):
        X = self.vector[:,0]
        Y = self.vector[:,1]
        x0, x1 = X.min(), X.max()
        y0, y1 = Y.min(), Y.max()
        return {
            "x0" : x0,
            "y0" : y0,
            "x1" : x1,
            "y1" : y1
        }

    def copy(self):
        return Arrow(self.__arr_info, self.__base_dimensions)

    def apply_perspective(self, TM):
        """
        Uses a transformation matrix to apply perspective effect in the vector points.
        Arguments:
            TM : Transformation matrix
        Return:
            p_arrow : Arrow with the applied perspective effect.
        """

        X = self.vector[:,0]
        Y = self.vector[:,1]
        m = X.shape[0]

        C = np.array([X, Y, np.ones((m), np.int32)])
            
        # C_perspective : matrix of the coordinates after the perspective was applied
        # X_perspective : X vector after the perspective was applied
        # Y_perspective : Y vector after the perspective was applied

        C_perspective = TM.dot(C)
        X_perspective = C_perspective[0,:] / C_perspective[2,:]
        Y_perspective = C_perspective[1,:] / C_perspective[2,:]   
        P = np.array([X_perspective, Y_perspective], dtype=np.int32).T

        # Creating a new arrow object:
        p_arrow = self.copy()
        p_arrow.__arrow_vector = P

        return p_arrow

class SuperArrow:
    """
    This is not exactly an arrow, but a set of arrows, which allow us much more personalization.
    
    Private properties:
        arr_info : informations about every arrow in the arrow set.
        base_dimensions : base_dimensions that every arrow in this arrow set will follow.
        arrow_vectors : list of arrow vectors.
        dx, dy : displacement values

    Public properties:
        label : reference to arr_info["label"].
        bounding_box : the bounding box of the arrow.
        displacement : the displacement in the arrow.

    This class has the responsibility to draw the arrows into the image, once it can get buggy with raw openCV.
    """

    def __init__(self, arr_info, base_dimensions):
        self.__arr_info = arr_info
        self.__base_dimensions = base_dimensions
        self.__arrow_vectors = []

        for subarrow_info in self.__arr_info["subarrows"]:
            arrow = Arrow(subarrow_info, self.__base_dimensions)
            arrow_vector = arrow.vector
            arrow_vector = self.__rotate_arrow(arrow_vector, subarrow_info["rotation"])
            arrow_vector = self.__apply_deltas(arrow_vector, subarrow_info)
            self.__arrow_vectors.append(arrow_vector)

        x0, y0, x1, y1 = self.bounding_box
        self.__dx, self.__dy = (x0 + x1) // 2, (y0 + y1) // 2 # Displacement default values

    def __apply_deltas(self, arrow_vector, subarrow_info):
        # Moves the vector in 2 dimensional area.
        delta_x = subarrow_info["delta_x"] * self.__base_dimensions[0]
        delta_y = subarrow_info["delta_y"] * self.__base_dimensions[1]
        delta_vector = np.array([[delta_x, delta_y]], np.int32)
        return arrow_vector + delta_vector

    def __define_rotation_offset(self, arrow_vector):
        X, Y = arrow_vector[:,0], arrow_vector[:,1]
        x0, y0, x1, y1 = X.min(), Y.min(), X.max(), Y.min()
        delta_x = (x1 - x0) // 2
        return (-x0, y1)

    def __rotate_arrow(self, arrow_vector, degrees):
        # Returns the vector after the rotation was applied.
        # RM : rotation matrix
        theta = 1 / 180 * np.pi * degrees
        RM = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
        rotated_arrow = RM.dot(arrow_vector.T)
        return rotated_arrow.T.astype(np.int32)

    def draw(self, img, color, dx=0, dy=0):
        # Draws every part of the arrow into the given image.
        for arrow_vector in self.__arrow_vectors:
            pts = arrow_vector.reshape((-1, 1, 2))
            img = cv.fillPoly(img, [pts], color)
        return img

    @property
    def label(self):
        return self.__arr_info["label"]

    @property
    def bounding_box(self):
        X = np.array([], np.int32)
        Y = np.array([], np.int32)
        for arrow_vector in self.__arrow_vectors:
            X = np.concatenate((X, arrow_vector[:,0]))
            Y = np.concatenate((Y, arrow_vector[:,1]))
        x0, x1 = X.min(), X.max()
        y0, y1 = Y.min(), Y.max()
        return (x0, y0, x1, y1)

    @property
    def displacement(self):
        return (self.__dx, self.__dy)

    @displacement.setter
    def displacement(self, values):
        delta_x, delta_y = values
        # Removing the past displacement:
        past_x, past_y = self.displacement
        delta_vector = np.array([[past_x, past_y]], np.int32)
        for i in range(len(self.__arrow_vectors)):
            self.__arrow_vectors[i] -= delta_vector
        # Adding the new displacement:
        delta_vector = np.array([[delta_x, delta_y]], np.int32)
        self.__dx, self.__dy = values
        for i in range(len(self.__arrow_vectors)):
            self.__arrow_vectors[i] += delta_vector

    def copy(self):
        return SuperArrow(self.__arr_info, self.__base_dimensions)

    def apply_perspective(self, TM):
        """
        Uses a transformation matrix to apply perspective effect in the vector points.
        Arguments:
            TM : Transformation matrix
        Return:
            p_arrow : Arrow with the applied perspective effect.
        """
        p_arrow = self.copy()
        p_arrow.__arrow_vectors = []
        for vector in self.__arrow_vectors:
            X = vector[:,0]
            Y = vector[:,1]
            m = X.shape[0]
            C = np.array([X, Y, np.ones((m), np.int32)])
            """ 
            C_perspective : matrix of the coordinates after the perspective was applied.
            X_perspective : X vector after the perspective was applied.
            Y_perspective : Y vector after the perspective was applied.
            """
            C_perspective = TM.dot(C)
            X_perspective = C_perspective[0,:] / C_perspective[2,:]
            Y_perspective = C_perspective[1,:] / C_perspective[2,:]   
            P = np.array([X_perspective, Y_perspective], dtype=np.int32).T
            # Inserting the new arrow at the composition:
            p_arrow.__arrow_vectors.append(P)
        return p_arrow

class ArrowCollection:
    """
    This class stores and manages SuperArrow objects.
    
    Private properties:
        base_dimensions : base_dimensions that every arrow in this arrow set will follow.
        arrows_info : dictionary of arrows informations.
    Public properties:
        labels : list of arrows labels.
    """
    def __init__(self, collection_path):
        """
        Arguments:
            collection_path : path to the json containing a list of paths to the SuperArrow json's
            base_dimensions : tuple of (base_width, base_height)
        """
        # Loading the arrows information:
        with open(collection_path, "r") as collection_file:
            collection = json.load(collection_file)
        arrows_folder, _ = os.path.split(collection_path)
        self.__arrows_info = {}
        for arrow_filename in collection:
            arrow_json_path = os.path.join(arrows_folder, arrow_filename)
            with open(arrow_json_path, "r") as arrow_file:
                arrow_json = json.load(arrow_file)
                self.__arrows_info[arrow_json["label"]] = arrow_json

    def get(self, arrow_label, base_dimensions):
        return SuperArrow(self.__arrows_info[arrow_label], base_dimensions)

    @property
    def labels(self):
        return tuple(self.__arrows_info.keys())
