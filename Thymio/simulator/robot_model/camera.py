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

    def robots_visible(self, x, y, q, objects):
        camera_vision = Polygon(
            [
                (x, y),
                (x + cos(q + self.fov / 2) * self.view_distance, (y + sin(q + self.fov / 2) * self.view_distance)),
                (x + cos(q + -self.fov / 2) * self.view_distance, (y + sin(q + -self.fov / 2) * self.view_distance))
            ])

        return any(camera_vision.covers(obj) for obj in objects)

    # either return l - left, m - middle, r - right or None
    def robot_relative_position(self, x, y, q, robot_body):
        # TODO: verify those positions are correct
        left_camera_view = Polygon(
            [
                (x, y),
                (x + cos(q + -self.fov / 2) * self.view_distance, (y + sin(q + -self.fov / 2) * self.view_distance)),
                (x + cos(q + -self.fov / 3) * self.view_distance, (y + sin(q + -self.fov / 3) * self.view_distance))
            ])
        if left_camera_view.covers(robot_body):
            return "l"
        middle_camera_view = Polygon(
            [
                (x, y),
                (x + cos(q + -self.fov / 3) * self.view_distance, (y + sin(q + -self.fov / 3) * self.view_distance)),
                (x + cos(q + self.fov / 3) * self.view_distance, (y + sin(q + self.fov / 3) * self.view_distance))
            ])
        if middle_camera_view.covers(robot_body):
            return "m"
        right_camera_view = Polygon(
            [
                (x, y),
                (x + cos(q + self.fov / 3) * self.view_distance, (y + sin(q + self.fov / 3) * self.view_distance)),
                (x + cos(q + self.fov / 2) * self.view_distance, (y + sin(q + self.fov / 2) * self.view_distance))
            ])
        if right_camera_view.covers(robot_body):
            return "r"
        return None

    def camera_range(self, x, y, q):
        return f"{x + cos(q + self.fov / 2) * self.view_distance}, {x + cos(q + -self.fov / 2) * self.view_distance}, {y + sin(q + self.fov / 2) * self.view_distance}, {y + sin(q + -self.fov / 2) * self.view_distance}"
