from numpy import sin, cos
from shapely.geometry import Polygon


class Camera:
    def __init__(self, W, H, fov, view_distance):
        self.W = W
        self.H = H
        self.fov = fov  # field of view in radians
        self.view_distance = view_distance

    def real_world_sensor_value(self, x, y, q, world):
        pass

    def objects_visible(self, x, y, q, objects):
        camera_vision = Polygon(
            [
                (x, y),
                (x + cos(q + self.fov / 2) * self.view_distance, (y + sin(q + self.fov / 2) * self.view_distance)),
                (x + cos(q + -self.fov / 2) * self.view_distance, (y + sin(q + -self.fov / 2) * self.view_distance))
            ])

        return any(camera_vision.covers(obj) for obj in objects)
