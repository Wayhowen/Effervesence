from abc import abstractmethod

from numpy import cos, sin


class Behavior:
    def __init__(self, simulator, controller):
        self.simulator = simulator
        self.controller = controller

        # used for speed measurment
        self.distances = []

    def step(self):
        self.simulator.step(self.controller)

    @abstractmethod
    def perform(self, step):
        pass

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.2}, {sin(self.controller.q) * 0.2}\n"
