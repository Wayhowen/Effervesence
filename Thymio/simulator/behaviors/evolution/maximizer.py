import numpy as np

from simulator.behaviors.behavior import Behavior
from numpy import cos, sin


class Maximizer(Behavior):
    def __init__(self, simulator, controller, q_table):
        super().__init__(simulator, controller)
        self._states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
        self._actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")

        self._q_table = q_table
        self._state = self._states.index("EXPLORE")
        self._fitness = 1

    def perform(self, step, other_controllers):
        action = np.argmax(self._q_table[self._state])
        self.perform_next_action(action)
        self._fitness += step

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(0.4, 0.4)
        elif action == 1:
            self.controller.drive(-0.8, 0.8)
        else:
            self.controller.drive(0.8, -0.8)

    def get_next_state(self):
        distance_to_objects = self.controller.distances_to_wall(self.simulator.world)

        if distance_to_objects[2] < 0.49:
            return self._states.index("INFRONT")
        elif distance_to_objects[0] < 0.49 or distance_to_objects[1] < 0.49:
            return self._states.index("LEFT")
        elif distance_to_objects[3] < 0.49 or distance_to_objects[4] < 0.49:
            return self._states.index("RIGHT")
        else:
            return self._states.index("EXPLORE")

    def callback(self):
        self._state = self.get_next_state()

    def save(self):
        pass

    def get_score(self):
        return self._fitness

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.09}, {sin(self.controller.q) * 0.09}\n"
