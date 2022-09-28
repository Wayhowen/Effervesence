from random import random

from sensor import Sensor


class Controller:
    def __init__(self, W, H):
        self.left_wheel_velocity: float = random()  # robot left wheel velocity in radians/s
        self.right_wheel_velocity: float = random()  # robot right wheel velocity in radians/s

        self.x = 0.0  # robot position in meters - x direction - positive to the right
        self.y = 0.0  # robot position in meters - y direction - positive up
        self.q = 0.0  # robot heading with respect to x-axis in radians

        # array of 5 sensors offset towards the front
        self.sensors = [Sensor(W, H, (0.35 * i)) for i in range(-2, 3)]

    def distances_to_wall(self, world):
        return [sensor.distance_to_wall(self.x, self.y, self.q, world) for sensor in self.sensors]
