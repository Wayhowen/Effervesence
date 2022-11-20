from simulator.behaviors.behavior import Behavior


class SpeedMeasurment(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step, other_controllers):
        self.distances.append(self.controller.distances_to_wall(self.simulator.world)[2])

        self.controller.left_wheel_velocity = 7.41
        self.controller.right_wheel_velocity = 7.41

        print(self.distances[0] - self.distances[-1])
