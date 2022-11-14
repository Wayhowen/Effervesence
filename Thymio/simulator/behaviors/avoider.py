import random

from simulator.behaviors.behavior import Behavior


class Avoider(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step, other_controllers):
        distances_to_objects = [self.controller.distances_to_objects(robot.controller.body)[2] for robot in other_controllers]
        if any(d and d < 0.09 for d in distances_to_objects):
            self.controller.left_wheel_velocity = 1.445
            self.controller.right_wheel_velocity = -1.445
            return
        elif self.controller.distances_to_wall(self.simulator.world)[2] < 0.09:
            self.controller.left_wheel_velocity = 1.445
            self.controller.right_wheel_velocity = -1.445
            return
        self.controller.left_wheel_velocity = random.uniform(0, 5.5)
        self.controller.right_wheel_velocity = random.uniform(0, 5.5)

        self.simulator.step(self.controller)

    def save(self):
        pass
