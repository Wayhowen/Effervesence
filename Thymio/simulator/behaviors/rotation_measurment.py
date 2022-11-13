from simulator.behaviors.behavior import Behavior


class RotationMeasurment(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step):
        self.distances.append(self.controller.q)

        self.controller.left_wheel_velocity = 5.5241
        self.controller.right_wheel_velocity = -5.5241

        # print rotation in radians every 4 secs
        if step % 48 == 0:
            print(abs(self.distances[-1] - self.distances[0]))
