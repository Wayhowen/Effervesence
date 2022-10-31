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
    states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
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
        print(prox_horizontal[2])
        if prox_horizontal[2] < 0.49:
            return states.index("INFRONT"), -1
        elif prox_horizontal[0] < 0.49 or prox_horizontal[1] < 0.49:
            return states.index("LEFT"), -1
        elif prox_horizontal[3] < 0.49 or prox_horizontal[4] < 0.49:
            return states.index("RIGHT"), -1
        else:
            return states.index("EXPLORE"), 1

    for cnt in range(10000):
        q_leaner.learn(step_function)
        # check collision with arena walls
        if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            break

    print(q_leaner.q_table)
            #
            # # check collision with arena walls
            # if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            #     break
