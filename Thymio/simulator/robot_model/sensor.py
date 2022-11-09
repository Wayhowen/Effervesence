from numpy import sin, cos, sqrt
from shapely.geometry import LineString

# sensor_values = {
#     "8.2": 1080,
#     "8": 1280,
#     "7.8": 1390,
#     "7.6": 1420,
#     "7.2": 1560,
#     "7": 1630,
#     "0": 4800
#
# }

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
    def __init__(self, W, H, offset: float):
        self.W = W
        self.H = H
        self.offset = offset  # offset of sensor from the middle in radians

    def real_world_sensor_value(self, x, y, q, world):
        distance_to_wall = self.distance_to_wall(x, y, q, world)
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
    def distance_to_wall(self, x, y, q, world):
        ray = LineString(
            [
                (x, y),
                (x + cos(q + self.offset) * 2 * (self.W + self.H), (y + sin(q + self.offset) * 2 * (self.W + self.H)))
            ])  # a line from robot to a point outside arena in direction of q
        s = world.intersection(ray)
        print(s)
        return sqrt((s.x - x) ** 2 + (s.y - y) ** 2)  # distance to wall
