from abc import abstractmethod
from typing import Tuple

from numpy import sin, cos, sqrt
from shapely.geometry import LineString, MultiPoint, Polygon, Point

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


class Sensor:
    def __init__(self, W, H, offset: float, position_getter):
        self.W = W
        self.H = H
        self.offset = offset  # offset of sensor from the middle in radians
        self.receiving_fov = 2.8  # 160 deg
        self.receiving_distance = 0.09
        self._position_getter = position_getter

    @abstractmethod
    def sensor_position(self) -> Tuple[float, float, float]:
        pass

    def real_world_sensor_value(self, world):
        distance_to_wall = self.distance_to_wall(world)
        distance_to_wall_3_numbers = float(str(distance_to_wall)[:4])
        if distance_to_wall_3_numbers > 0.09:
            return 0
        elif distance_to_wall_3_numbers == 0.09:
            return sensor_values["9"]
        elif distance_to_wall < 0.00:
            return sensor_values["0"]
        distance_cm = int(str(distance_to_wall)[3])
        table_cm_lookup = sensor_values[f"{distance_cm}"]
        table_cm_lookup_plus_one = sensor_values[f"{distance_cm + 1}"]
        difference = table_cm_lookup_plus_one - table_cm_lookup

        percentage_of_higher_value = (float(f"0.0{distance_cm + 1}") - distance_to_wall) / float(f"0.0{distance_cm + 1}")
        res = table_cm_lookup + (percentage_of_higher_value * difference)
        return res

    """very precise simulator distance"""
    def distance_to_wall(self, world):
        x, y, q = self.sensor_position()
        ray = LineString(
            [
                (x, y),
                (x + cos(q) * 4 * (self.W + self.H), (y + sin(q) * 4 * (self.W + self.H)))
            ])  # a line from robot to a point outside arena in direction of q
        s = world.intersection(ray)
        if s.is_empty:
            return float('inf')
        if type(s) is MultiPoint:
            mult = list(s.geoms)
            closest_side = list(mult[0].coords)[0]
        else:
            closest_side = list(s.coords)[0]
        return sqrt((closest_side[0] - x) ** 2 + (closest_side[1] - y) ** 2)  # distance to wall

    def distance_to_object(self, other_object):
        x, y, q = self.sensor_position()
        ray = LineString(
            [
                (x, y),
                (x + cos(q) * 2 * (self.W + self.H), (y + sin(q) * 2 * (self.W + self.H)))
            ])  # a line from robot to a point outside arena in direction of q
        s = other_object.intersection(ray)
        if s.is_empty:
            return float('inf')
        if type(s) is MultiPoint:
            mult = list(s.geoms)
            closest_side = list(mult[0].coords)[0]
        else:
            closest_side = list(s.coords)[0]
        return sqrt((closest_side[0] - x) ** 2 + (closest_side[1] - y) ** 2)  # distance to wall

    def can_receive(self, sensor_point: Point):
        x, y, q = self.sensor_position()
        sensor_vision = Polygon(
            [
                (x, y),
                (x + cos(q + self.receiving_fov / 2) * self.receiving_distance, (y + sin(q + self.receiving_fov / 2) * self.receiving_distance)),
                (x + cos(q + -self.receiving_fov / 2) * self.receiving_distance, (y + sin(q + -self.receiving_fov / 2) * self.receiving_distance))
            ])
        return sensor_vision.covers(sensor_point)
