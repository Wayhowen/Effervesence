from numpy import cos, sin
from shapely.geometry import Point
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
from simulator.robot_model.controller import Controller
from simulator import Simulator


class Behaviors:
    def __init__(self):
        self.simulator = Simulator()
        self.controller = Controller(self.simulator.W, self.simulator.H)

        # used for speed measurment
        self.distances = []

    def step(self):
        self.simulator.step(self.controller)

    def wall_avoidance(self, step):
        distance = self.controller.distances_to_wall(self.simulator.world)[2]
        # simple controller - change direction of wheels every 10 seconds (100*robot_timestep) unless close to wall then turn on spot
        if distance < 0.1:
            self.controller.left_wheel_velocity = 1.445
            self.controller.right_wheel_velocity = -1.445
        else:
            if step % 100 == 0:
                self.controller.left_wheel_velocity = 1.445
                self.controller.right_wheel_velocity = 1.445

    def speed_measurment(self, step):
        self.distances.append(self.controller.distances_to_wall(self.simulator.world)[2])

        self.controller.left_wheel_velocity = 1.445
        self.controller.right_wheel_velocity = 1.445

        # print distance travelled in meters every 4 secs
        if step % 40 == 0:
            print(abs(self.distances[-1] - self.distances[0]))

    def rotation_measurment(self, step):
        self.distances.append(self.controller.q)

        self.controller.left_wheel_velocity = 5.5241
        self.controller.right_wheel_velocity = -5.5241

        # print rotation in radians every 4 secs
        if step % 48 == 0:
            print(abs(self.distances[-1] - self.distances[0]))

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.2}, {sin(self.controller.q) * 0.2}\n"


if __name__ == '__main__':
    behaviors = Behaviors()
    with open("animator/trajectory.dat", "w") as file:
        for cnt in range(5000):
            # simple single-ray sensor
            try:
                behaviors.rotation_measurment(cnt)

                # step simulation
                behaviors.step()

                # # check collision with arena walls
                # if controller.on_the_line(simulator.world):
                #     file.write(f"{controller.x}, {controller.y}, {cos(controller.q) * 0.2}, {sin(controller.q) * 0.2}\n")
                #     break

                if cnt % 50 == 0:
                    file.write(behaviors.position)
            except AttributeError:
                file.write(behaviors.position)
                print("out of bounds")
                break