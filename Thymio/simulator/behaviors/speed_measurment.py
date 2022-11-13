from simulator.behaviors.behavior import Behavior


class SpeedMeasurment(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step):
        self.distances.append(self.controller.distances_to_wall(self.simulator.world)[2])

        self.controller.left_wheel_velocity = 1.445
        self.controller.right_wheel_velocity = 1.445

        # print distance travelled in meters every 4 secs
        if step % 40 == 0:
            print(abs(self.distances[-1] - self.distances[0]))
