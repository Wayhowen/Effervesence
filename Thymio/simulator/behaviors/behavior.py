from abc import abstractmethod
from typing import List

from numpy import cos, sin


class Behavior:
    def __init__(self, simulator, controller):
        self.simulator = simulator
        self.controller = controller

        # used for speed measurment
        self.distances = []
        self._score = 0
        self._tagged = False

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

    def try_tagging(self, other_robot: 'Behavior') -> bool:
        if not other_robot.is_tagged and not other_robot.is_in_safezone:
            other_robot._tagged = True
            return True
        return False

    @property
    def is_in_safezone(self):
        return self.controller.in_the_safezone(self.simulator.world, self.simulator.safezone)

    @property
    def is_tagged(self) -> bool:
        return self._tagged

    def robot_relative_positions_from_camera(self, robots: List['Behavior']):
        return self.controller.robots_relative_positions_from_camera(robots)

