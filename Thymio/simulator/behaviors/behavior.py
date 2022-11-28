from abc import abstractmethod
from typing import List, Tuple

from numpy import cos, sin
from shapely.geometry import Point

from simulator.robot_model.sensor.sensor import Sensor


class Behavior:
    def __init__(self, simulator, controller):
        self.simulator = simulator
        self.controller = controller

        # used for speed measurment
        self.distances = []
        self._score = 0
        self.tagged = False
        self.forced_out_of_safezone = 0

        # uninitialized is jellow
        self._color = "#EFFF00"
        self._colors = {
            "seeking": "#FF0000",
            "safe_seeking": "#FF9100",
            "avoiding": "#2B00FF",
            "safe_avoiding": "#00FF22",
            "tagged": "#CD00FF"
        }

    @property
    def color(self):
        return self._color

    def step(self):
        self.simulator.step(self.controller)

    @abstractmethod
    def perform(self, step, other_controllers):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def callback(self, step: int, other_robots):
        pass

    @abstractmethod
    def get_score(self):
        pass

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.09}, {sin(self.controller.q) * 0.09}"

    @property
    def camera_range(self):
        return self.controller.get_camera_range()

    def try_tagging(self, other_robot: 'Behavior', sensor_indexes: List[int]) -> bool:
        sensors_positions = [self.controller.sensors[i].sensor_position() for i in sensor_indexes]
        if not other_robot.is_tagged and not other_robot.is_in_safezone and other_robot.can_receive(sensors_positions):
            other_robot.tagged = True
            return True
        return False

    def try_forcing_out_of_safezone(self, other_robot, sensor_indexes: List[int], step: int):
        sensors_positions = [self.controller.sensors[i].sensor_position() for i in sensor_indexes]
        if other_robot.is_in_safezone and other_robot.can_receive(sensors_positions):
            other_robot.forced_out_of_safezone = step

    @property
    def is_in_safezone(self):
        return self.controller.in_the_safezone(self.simulator.safezone)

    @property
    def is_tagged(self) -> bool:
        return self.tagged

    def robot_relative_positions_from_camera(self, robots: List['Behavior']):
        return self.controller.robots_relative_positions_from_camera(robots)

    def can_receive(self, sensors: List[Tuple[float, float, float]]):
        return any(self.controller.can_receive(Point(position[0], position[1])) for position in sensors)

