from simulator.behaviors.behavior import Behavior


class RotationMeasurment(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step, other_controllers):
        self.distances.append(self.controller.q)

        self.controller.left_wheel_velocity = 11.976
        self.controller.right_wheel_velocity = -11.976

        print(self.distances[0] - self.distances[-1])

