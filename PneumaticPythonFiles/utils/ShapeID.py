import cv2
import numpy as np


class DotParameters:
    """
    This is the class which is used to define all the parameters for the comparisons
    """
    
    def __init__(self, minAreaDot, maxAreaDot, minEcc, maxEcc, maxDist):
        self.minArea = minAreaDot
        self.maxArea = maxAreaDot
        self.minEcc = minEcc
        self.maxEcc = maxEcc
        self.maxDist = maxDist

