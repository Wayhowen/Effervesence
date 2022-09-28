from numpy import cos, sin
from shapely.geometry import Point
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
from controller import Controller
from simulator import Simulator

simulator = Simulator()
controller = Controller(simulator.W, simulator.H)

with open("trajectory.dat", "w") as file:
    for cnt in range(5000):
        # simple single-ray sensor
        distance = controller.distances_to_wall(simulator.world)[2]

        # simple controller - change direction of wheels every 10 seconds (100*robot_timestep) unless close to wall then turn on spot
        if distance < 0.5:
            controller.left_wheel_velocity = -0.4
            controller.right_wheel_velocity = 0.4
        else:
            if cnt % 100 == 0:
                controller.left_wheel_velocity = random()
                controller.right_wheel_velocity = random()

        # step simulation
        simulator.step(controller)

        # check collision with arena walls
        if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            break

        if cnt % 50 == 0:
            file.write(f"{controller.x}, {controller.y}, {cos(controller.q) * 0.2}, {sin(controller.q)}\n")
