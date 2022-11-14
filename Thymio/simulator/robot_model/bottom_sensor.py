from numpy import sin, cos
from shapely.geometry import LineString, Polygon, Point


sensor_values = {
    "9": 1200,
    "8": 1600,
    "7": 2000,
    "6": 2250,
    "5": 2500,
    "4": 3000,
    "3": 3750,
    "2": 4200,
    "1": 4350,
    "0": 4250
}


class BottomSensor:
    def __init__(self, W, H, offset: float):
        self.W = W
        self.H = H
        self.offset = offset  # offset of sensor from the middle in radians

    def real_world_sensor_value(self, x, y, q, world):
        pass

    def is_on_the_line(self, x, y, q, world, bounds) -> bool:
        pos = Point(x,y)
        if bounds.contains(pos) and not Polygon(world).contains(pos):
            return True
        return False
