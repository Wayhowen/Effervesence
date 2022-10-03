from numpy import sin, cos, sqrt
from shapely.geometry import LineString

map = {
    "8.2": 1080,
    "8": 1280,
    "7.8": 1390,
    "7.6": 1420,
    "7.2": 1560,
    "7": 1630,
    "0": 4800

}


class Sensor:
    def __init__(self, W, H, offset: float):
        self.W = W
        self.H = H
        self.offset = offset # offset of sensor from the middle in radians

    def distance_to_wall(self, x, y, q, world):
        ray = LineString(
            [
                (x, y),
                (x + cos(q + self.offset) * 2 * (self.W + self.H), (y + sin(q + self.offset) * 2 * (self.W + self.H)))
            ])  # a line from robot to a point outside arena in direction of q
        s = world.intersection(ray)
        return sqrt((s.x - x) ** 2 + (s.y - y) ** 2)  # distance to wall