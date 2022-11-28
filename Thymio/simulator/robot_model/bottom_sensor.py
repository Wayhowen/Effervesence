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
    def __init__(self, W, H, position_getter, forward_offset_cm, side_offset_cm, side_offset_radians):
        self.W = W
        self.H = H
        self._position_getter = position_getter

        self._forward_offset_cm = forward_offset_cm
        self._side_offset_cm = side_offset_cm
        self._side_offset_radians = side_offset_radians

    def _sensor_position(self):
        x, y, q = self._position_getter()

        x = x + cos(q) * self._forward_offset_cm
        y = y + sin(q) * self._forward_offset_cm

        # move to the sides
        x = x + cos(q + self._side_offset_radians) * self._side_offset_cm
        y = y + sin(q + self._side_offset_radians) * self._side_offset_cm

        return x, y, q

    def real_world_sensor_value(self, world):
        pass

    def is_on_the_line(self, bounds) -> bool:
        x, y, _ = self._position_getter()
        pos = Point(x, y)
        if bounds.covers(pos):
            return True
        return False
