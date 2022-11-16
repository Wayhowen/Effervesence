import random

from simulator.behaviors.behavior import Behavior


class Tagger(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []
        self._tagged = True

    def perform(self, step, other_controllers):
        # drive around
        for robot in other_controllers:
            distances_to_objects = self.controller.distances_to_objects(robot.controller.body)
            if any(d and d < 0.09 for d in distances_to_objects):
                tagging_success = self.try_tagging(robot)

        if self.controller.distances_to_wall(self.simulator.world)[2] < 0.09:
            self.controller.drive(-1.445, 1.445)
            return
        self.controller.drive(random.uniform(0, 5.5), random.uniform(0, 5.5))

    def save(self):
        pass
