from random import random

from shapely.geometry import LineString
from numpy import sin, cos, sqrt


class Controller:
    def __init__(self, W, H):
        self.left_wheel_velocity: float = random()  # robot left wheel velocity in radians/s
        self.right_wheel_velocity: float = random()  # robot right wheel velocity in radians/s

        self.x = 0.0  # robot position in meters - x direction - positive to the right
        self.y = 0.0  # robot position in meters - y direction - positive up
        self.q = 0.0  # robot heading with respect to x-axis in radians

        self.middle_ray = LineString(
            [
                (self.x, self.y),
                (self.x + cos(self.q) * 2 * (W + H), (self.y + sin(self.q) * 2 * (W + H)))
            ])  # a line from robot to a point outside arena in direction of q

    def distance_to_wall(self, world):
        s = world.intersection(self.middle_ray)
        return sqrt((s.x - self.x) ** 2 + (s.y - self.y) ** 2)  # distance to wall