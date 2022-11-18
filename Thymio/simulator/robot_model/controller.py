from random import random

from shapely.geometry import Point, Polygon

from .bottom_sensor import BottomSensor
from .camera import Camera
from .side_sensor import SideSensor


class Controller:
    def __init__(self, W, H, x=0.0, y=0.0, q=0.0, robot_radius=0.0575):
        self.left_wheel_velocity: float = random()  # robot left wheel velocity in radians/s
        self.right_wheel_velocity: float = random()  # robot right wheel velocity in radians/s
        self._robot_radius = robot_radius

        self.x = x  # robot position in meters - x direction - positive to the right
        self.y = y  # robot position in meters - y direction - positive up
        self.q = q  # robot heading with respect to x-axis in radians

        # array of 5 sensors offset towards the front
        self.sensors = [SideSensor(W, H, (0.35 * i)) for i in range(-2, 3)]

        # 1 sensor at the back, simplification of 2
        self.sensors.append(SideSensor(W, H, 3.14))

        self.bottom_sensor = BottomSensor(W, H, 0)
        self.camera = Camera(W, H, 2, 0.5)

    @property
    def body(self):
        return Point(self.x, self.y).buffer(self._robot_radius)

    def distances_to_wall(self, world):
        return [sensor.distance_to_wall(self.x, self.y, self.q, world) for sensor in self.sensors]

    def distances_to_objects(self, other_robot):
        return [sensor.distance_to_object(self.x, self.y, self.q, other_robot) for sensor in self.sensors]

    def values_of_sensors(self, world):
        return [sensor.real_world_sensor_value(self.x, self.y, self.q, world) for sensor in self.sensors]

    def on_the_line(self, world, bounds) -> bool:
        pos = Point(self.x, self.y)
        return self.bottom_sensor.is_on_the_line(self.x, self.y, bounds) and not Polygon(world).covers(pos)

    def in_the_safezone(self, world, safezone):
        return self.bottom_sensor.is_on_the_line(self.x, self.y, safezone)

    def drive(self, left_wheel_velocity, right_wheel_velocity):
        self.left_wheel_velocity = left_wheel_velocity
        self.right_wheel_velocity = right_wheel_velocity
    
    def get_speed(self):
        return self.left_wheel_velocity, self.left_wheel_velocity
