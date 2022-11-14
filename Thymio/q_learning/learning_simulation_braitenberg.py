import pkgutil

import numpy as np
from shapely.geometry import Point
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
from q_learning.q_learning import QLearner
from simulator.robot_model.controller import Controller
from simulator.simulator import Simulator


if __name__ == '__main__':
    states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
    actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")
    qt = np.array([[ 3.10624095, 8.38157012, -12.93252732],
                    [ 10.01043967, 10.02261024, -0.67002202],
                    [ -1.68985408, 12.18825473, 3.78742241],
                    [ 0.94576732, -15.20442771, -11.75258557]])

    q_leaner = QLearner(states, actions, states.index("EXPLORE"), qt, 1.0)
    simulator = Simulator()
    controller = Controller(simulator.W, simulator.H)


    def step_function(action):
        reward = 0
        prox_horizontal = controller.distances_to_wall(simulator.world)

        if action == 0:
            controller.drive(0.4, 0.4)
            if prox_horizontal[2] < 0.49:
                reward -= 10
            else:
                reward += 20
        elif action == 1:
            controller.drive(-0.8, 0.8)
            if prox_horizontal[0] > 0.49 or prox_horizontal[1] > 0.49:
                reward -= 10
            else:
                reward += 10    
        else:
            controller.drive(0.8, -0.8)
            if prox_horizontal[3] > 0.49 or prox_horizontal[4] > 0.49:
                reward -= 10
            else:
                reward += 10 
        # step simulation
        simulator.step(controller)

        
        print(prox_horizontal[2])
        if prox_horizontal[2] < 0.49:
            return states.index("INFRONT"), reward
        elif prox_horizontal[0] < 0.49 or prox_horizontal[1] < 0.49:
            return states.index("LEFT"), reward
        elif prox_horizontal[3] < 0.49 or prox_horizontal[4] < 0.49:
            return states.index("RIGHT"), reward
        else:
            return states.index("EXPLORE"), reward

    with open("../animator/trajectory.dat", "w") as file:
        for cnt in range(10000):
            q_leaner.choose_next_action(step_function)
            # check collision with arena walls
            if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
                break
            
            if cnt % 50 == 0:
                file.write(f"{controller.x}, {controller.y}, {np.cos(controller.q) * 0.2}, {np.sin(controller.q) * 0.2}\n")

    print(q_leaner.q_table)
    q_leaner.save_q_table()
            #
            # # check collision with arena walls
            # if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            #     break
