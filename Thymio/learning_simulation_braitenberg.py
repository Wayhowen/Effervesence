import pkgutil

from numpy import cos, sin
from shapely.geometry import Point
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
from q_learning import QLearner
from simulator.robot_model.controller import Controller
from simulator.simulator import Simulator


if __name__ == '__main__':
    states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE", "BACKINGUP", "TURNING")
    actions = ("GOFORWARDS", "GOBACKWARDS", "GOLEFT", "GORIGHT")
    q_leaner = QLearner(states, actions, states.index("EXPLORE"))
    simulator = Simulator()
    controller = Controller(simulator.W, simulator.H)


    def step_function(action):
        if action == 0:
            controller.drive(0.4, 0.4)
        elif action == 1:
            controller.drive(-0.4, -0.4)
        elif action == 2:
            controller.drive(-0.4, 0.4)
        else:
            controller.drive(0.4, -0.4)
        # step simulation
        simulator.step(controller)

        prox_horizontal = controller.distances_to_wall(simulator.world)
        prox_odom_l, prox_odom_r = controller.get_speed()
        print(prox_horizontal[2])
        if prox_horizontal[2] < 0.49:
            return states.index("INFRONT"), 5
        elif prox_horizontal[0] < 0.49 or prox_horizontal[1] < 0.49:
            return states.index("LEFT"), 10
        elif prox_horizontal[3] < 0.49 or prox_horizontal[4] < 0.49:
            return states.index("RIGHT"), 10
        elif prox_odom_l+prox_odom_r < 0.0 :
            return states.index("BACKINGUP"), 1
        elif (prox_odom_l < 0.0 and prox_odom_r > 0.0) or (prox_odom_l > 0.0 and prox_odom_r < 0.0):
            return states.index("TURNING"), 2
        else:
            return states.index("EXPLORE"), 20

    with open("animator/trajectory.dat", "w") as file:
        for cnt in range(10000):
            q_leaner.learn(step_function)
            # check collision with arena walls
            if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
                break
            
            if cnt % 50 == 0:
                file.write(f"{controller.x}, {controller.y}, {cos(controller.q) * 0.2}, {sin(controller.q) * 0.2}\n")

    print(q_leaner.q_table)
            #
            # # check collision with arena walls
            # if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            #     break
