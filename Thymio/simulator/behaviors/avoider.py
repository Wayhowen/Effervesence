import random

from simulator.behaviors.behavior import Behavior


class Avoider(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []
        self._color = self._colors["avoiding"]

    def perform(self, step, other_controllers):
        if self.is_in_safezone:
            self.controller.drive(0, 0)
            self._color = self._colors["avoiding_safe"]
            return
        if self.is_tagged or self.is_in_safezone:
            self.controller.drive(0, 0)
            self._color = self._colors["tagged"]
            return
        distances_to_objects = [self.controller.distances_to_objects(robot.controller.body)[2] for robot in other_controllers]
        if any(d and d < 0.09 for d in distances_to_objects):
            self.controller.drive(1.445, -1.445)
            return
        elif self.controller.distances_to_wall(self.simulator.world)[2] < 0.09:
            self.controller.drive(1.445, -1.445)
            return
        self.controller.drive(random.uniform(0, 5.5), random.uniform(0, 5.5))

    def save(self):
        pass
