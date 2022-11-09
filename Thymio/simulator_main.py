from numpy import cos, sin
from shapely.geometry import Point
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
from simulator.robot_model.controller import Controller
from simulator import Simulator


if __name__ == '__main__':
    simulator = Simulator()
    controller = Controller(simulator.W, simulator.H)
    with open("animator/trajectory.dat", "w") as file:
        for cnt in range(5000):
            # simple single-ray sensor
            try:
                on_the_line = controller.on_the_line(simulator.world)
                # simple controller - change direction of wheels every 10 seconds (100*robot_timestep) unless close to wall then turn on spot
                if on_the_line:
                    controller.left_wheel_velocity = -0.4
                    controller.right_wheel_velocity = -0.4
                else:
                    distance = controller.distances_to_wall(simulator.world)[2]

                    if cnt % 100 == 0:
                        controller.left_wheel_velocity = random()
                        controller.right_wheel_velocity = random()

                # step simulation
                simulator.step(controller)

                # check collision with arena walls
                if on_the_line:
                    file.write(f"{controller.x}, {controller.y}, {cos(controller.q) * 0.2}, {sin(controller.q) * 0.2}\n")
                    break

                if cnt % 50 == 0:
                    file.write(f"{controller.x}, {controller.y}, {cos(controller.q) * 0.2}, {sin(controller.q) * 0.2}\n")
            except AttributeError:
                file.write(f"{controller.x}, {controller.y}, {cos(controller.q) * 0.2}, {sin(controller.q) * 0.2}\n")
                print("out of bounds")
                break