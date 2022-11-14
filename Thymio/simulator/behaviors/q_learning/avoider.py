import pkgutil

import numpy as np
from shapely.geometry import Point

from q_learning.q_learning import QLearner
from simulator.behaviors.behavior import Behavior
from simulator.robot_model.controller import Controller
from simulator.simulator import Simulator

from abc import abstractmethod

from numpy import cos, sin


class Avoider(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        self._states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
        self._actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")
        self._q_leaner = QLearner(self._states, self._actions, self._states.index("EXPLORE"))

    def perform(self, step, other_controllers):
        self._q_leaner.learn(self.step_function)

    def step_function(self, action):
        reward = 0
        distance_to_objects = self.controller.distances_to_wall(self.simulator.world)

        if action == 0:
            self.controller.drive(0.4, 0.4)
            if distance_to_objects[2] < 0.49:
                reward -= 10
            else:
                reward += 20
        elif action == 1:
            self.controller.drive(-0.8, 0.8)
            if distance_to_objects[0] > 0.49 or distance_to_objects[1] > 0.49:
                reward -= 10
            else:
                reward += 10
        else:
            self.controller.drive(0.8, -0.8)
            if distance_to_objects[3] > 0.49 or distance_to_objects[4] > 0.49:
                reward -= 10
            else:
                reward += 10
                # step simulation

        self.simulator.step(self.controller)

        if distance_to_objects[2] < 0.49:
            return self._states.index("INFRONT"), reward
        elif distance_to_objects[0] < 0.49 or distance_to_objects[1] < 0.49:
            return self._states.index("LEFT"), reward
        elif distance_to_objects[3] < 0.49 or distance_to_objects[4] < 0.49:
            return self._states.index("RIGHT"), reward
        else:
            return self._states.index("EXPLORE"), reward

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.09}, {sin(self.controller.q) * 0.09}\n"
