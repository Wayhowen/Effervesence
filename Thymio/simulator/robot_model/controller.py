from random import random
from typing import List, Tuple, Dict

from shapely.geometry import Point, Polygon

from .bottom_sensor import BottomSensor
from .camera import Camera
from .sensor.back_sensor import BackSensor
from .sensor.sensor import Sensor
from .sensor.side_sensor import SideSensor
from ..behaviors.behavior import Behavior


class Controller:
    def __init__(self, W, H, x=0.0, y=0.0, q=0.0, robot_radius=0.0575):
        self.left_wheel_velocity: float = random()  # robot left wheel velocity in radians/s
        self.right_wheel_velocity: float = random()  # robot right wheel velocity in radians/s
        self._robot_radius = robot_radius

        self.x = x  # robot position in meters - x direction - positive to the right
        self.y = y  # robot position in meters - y direction - positive up
        self.q = q  # robot heading with respect to x-axis in radians

        # array of 5 sensors offset towards the front
        self.sensors: List[Sensor] = [
            SideSensor(W, H, (0.35 * i), self._position_getter, sensor_forward_offset=0.08) for i in range(-2, 3)
        ]

        # 2 sensors at the back
        # TODO: they may be unused yet
        self.sensors.append(BackSensor(W, H, 3.14, self._position_getter,
                                       backward_offset_cm=0.062, side_offset_cm=0.031, side_offset_radians=-1.57))
        self.sensors.append(BackSensor(W, H, 3.14, self._position_getter,
                                       backward_offset_cm=0.062, side_offset_cm=0.031, side_offset_radians=1.57))

        self.bottom_sensor_left = BottomSensor(
            W, H, self._position_getter, forward_offset_cm=0.075, side_offset_cm=0.011, side_offset_radians=-1.57
        )
        self.bottom_sensor_right = BottomSensor(
            W, H, self._position_getter, forward_offset_cm=0.075, side_offset_cm=0.011, side_offset_radians=1.57
        )
        self.camera = Camera(W, H, 1.4, 1)

    @property
    def body(self):
        return Point(self.x, self.y).buffer(self._robot_radius)

    def _position_getter(self):
        return self.x, self.y, self.q

    def distances_to_wall(self, world):
        return [sensor.distance_to_wall(world) for sensor in self.sensors]

    def distances_to_objects(self, other_robot):
        return [sensor.distance_to_object(other_robot) for sensor in self.sensors]

    def values_of_sensors(self, world):
        return [sensor.real_world_sensor_value(world) for sensor in self.sensors]

    def on_the_line(self, world, bounds) -> Tuple[bool, bool]:
        pos = Point(self.x, self.y)
        left_on_line = self.bottom_sensor_left.is_on_the_line(bounds)
        right_on_line = self.bottom_sensor_right.is_on_the_line(bounds)
        is_in_the_inner_circle = Polygon(world).covers(pos)

        return left_on_line and not is_in_the_inner_circle, right_on_line and not is_in_the_inner_circle

    def robots_relative_positions_from_camera(self, robots: List[Behavior]) -> Dict[str, Behavior]:
        return self.camera.robot_relative_position(self.x, self.y, self.q, robots)

    def in_the_safezone(self, safezone):
        return self.bottom_sensor_left.is_on_the_line(safezone)

    def drive(self, left_wheel_velocity, right_wheel_velocity):
        self.left_wheel_velocity = left_wheel_velocity
        self.right_wheel_velocity = right_wheel_velocity
    
    def get_speed(self):
        return self.left_wheel_velocity, self.left_wheel_velocity

    def get_camera_range(self):
        return self.camera.camera_range(self.x, self.y, self.q)

    def can_receive(self, sensor_point: Point):
        return any(s.can_receive(sensor_point) for s in self.sensors)
