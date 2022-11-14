from abc import abstractmethod

from numpy import cos, sin


class Behavior:
    def __init__(self, simulator, controller):
        self.simulator = simulator
        self.controller = controller

        # used for speed measurment
        self.distances = []
        self._score = 0

    def step(self):
        self.simulator.step(self.controller)

    @abstractmethod
    def perform(self, step, other_controllers):
        pass

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.09}, {sin(self.controller.q) * 0.09}\n"
