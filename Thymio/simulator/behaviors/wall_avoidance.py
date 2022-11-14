from simulator.behaviors.behavior import Behavior


class WallAvoidance(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        # used for speed measurment
        self.distances = []

    def perform(self, step):
        distance = self.controller.distances_to_wall(self.simulator.world)[2]
        # simple controller - change direction of wheels every 10 seconds (100*robot_timestep) unless close to wall then turn on spot
        if distance < 0.1:
            self.controller.left_wheel_velocity = 1.445
            self.controller.right_wheel_velocity = -1.445
        else:
            if step % 100 == 0:
                self.controller.left_wheel_velocity = 1.445
                self.controller.right_wheel_velocity = 1.445
