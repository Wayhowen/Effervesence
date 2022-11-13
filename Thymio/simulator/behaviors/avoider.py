from simulator.behaviors.behavior import Behavior


class Avoider(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step):
        self.controller.left_wheel_velocity = 1.445
        self.controller.right_wheel_velocity = -1.445
        print(self.controller.distances_to_objects(self.controller.body))
