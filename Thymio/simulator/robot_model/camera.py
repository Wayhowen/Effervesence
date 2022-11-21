from typing import List, Dict

from numpy import sin, cos, sqrt
from shapely.geometry import Polygon, LineString, MultiPoint

from simulator.behaviors.behavior import Behavior


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
    def robot_relative_position(self, x, y, q, robots: List[Behavior]) -> Dict[str, Behavior]:
        robot_positions = {
            "l": [],
            "m": [],
            "r": []
        }
        for robot in robots:
            left_camera_view = Polygon(
                [
                    (x, y),
                    (x + cos(q + -self.fov / 2) * self.view_distance, (y + sin(q + -self.fov / 2) * self.view_distance)),
                    (x + cos(q + -self.fov / 3) * self.view_distance, (y + sin(q + -self.fov / 3) * self.view_distance))
                ])
            if left_camera_view.covers(robot.controller.body):
                robot_positions["l"].append(robot)
            middle_camera_view = Polygon(
                [
                    (x, y),
                    (x + cos(q + -self.fov / 3) * self.view_distance, (y + sin(q + -self.fov / 3) * self.view_distance)),
                    (x + cos(q + self.fov / 3) * self.view_distance, (y + sin(q + self.fov / 3) * self.view_distance))
                ])
            if middle_camera_view.covers(robot.controller.body):
                robot_positions["m"].append(robot)
            right_camera_view = Polygon(
                [
                    (x, y),
                    (x + cos(q + self.fov / 3) * self.view_distance, (y + sin(q + self.fov / 3) * self.view_distance)),
                    (x + cos(q + self.fov / 2) * self.view_distance, (y + sin(q + self.fov / 2) * self.view_distance))
                ])
            if right_camera_view.covers(robot.controller.body):
                robot_positions["r"].append(robot)

        selected_robots = self._filter_invisible_robots(x, y, robot_positions)
        return selected_robots

    def _filter_invisible_robots(self, x, y, robots: Dict[str, List[Behavior]]) -> Dict[str, Behavior]:
        return {
            "l": min([(robot, self._distance_to_object(x, y, robot)) for robot in robots["l"]], key=lambda a: a[1])[0] if robots["l"] else None,
            "m": min([(robot, self._distance_to_object(x, y, robot)) for robot in robots["m"]], key=lambda a: a[1])[0] if robots["m"] else None,
            "r": min([(robot, self._distance_to_object(x, y, robot)) for robot in robots["r"]], key=lambda a: a[1])[0] if robots["r"] else None
        }

    def camera_range(self, x, y, q):
        return f"{x + cos(q + self.fov / 2) * self.view_distance}, {x + cos(q + -self.fov / 2) * self.view_distance}, {y + sin(q + self.fov / 2) * self.view_distance}, {y + sin(q + -self.fov / 2) * self.view_distance}"

    # copied for now
    def _distance_to_object(self, x, y, other_robot: Behavior):
        ray = LineString(
            [
                (x, y),
                (other_robot.controller.x, other_robot.controller.y)
            ])  # a line from robot to an other robot
        s = other_robot.controller.body.intersection(ray)
        if s.is_empty:
            return float('inf')
        if type(s) is MultiPoint:
            mult = list(s.geoms)
            closest_side = list(mult[0].coords)[0]
        else:
            closest_side = list(s.coords)[0]
        return sqrt((closest_side[0] - x) ** 2 + (closest_side[1] - y) ** 2)  # distance to wall