import numpy as np

from simulator.behaviors.behavior import Behavior
from numpy import cos, sin


class AvoiderMaximizer(Behavior):
    def __init__(self, simulator, controller, q_table, total_steps):
        super().__init__(simulator, controller)
        self._states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE", "LINE", "BEHIND")
        self._actions = ("GOFORWARDS", "GOLEFT", "GORIGHT", "REVERSE")

        self._q_table = q_table
        self._total_steps = total_steps
        self._state = self._states.index("EXPLORE")
        self._fitness = 1
        self.distances_to_objects = []

    def perform(self, step, other_controllers):
        self.distances_to_objects = [self.controller.distances_to_objects(robot.controller.body) for robot in
                                     other_controllers]
        action = np.argmax(self._q_table[self._state])
        self.perform_next_action(action)
        self._fitness += 1

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(7.41, 7.41)
        elif action == 1:
            self.controller.drive(-11.976, 11.976)
        elif action == 2:
            self.controller.drive(11.976, -11.976)
        elif action == 3:
            self.controller.drive(-7.41, -7.41)

    def get_next_state(self):
        on_line = self.controller.on_the_line(self.simulator.world, self.simulator.bounds)
        # Get the closest reading of those returned
        closest_reading = min([(x, sum(x)) for x in self.distances_to_objects], key=lambda reading: reading[1])[0]

        if on_line:
            self._fitness -= 10
            return self._states.index("LINE")
        elif closest_reading[2] < 0.09:
            self._fitness += 15
            return self._states.index("INFRONT")
        elif closest_reading[0] < 0.09 or closest_reading[1] < 0.09:
            self._fitness += 5
            return self._states.index("LEFT")
        elif closest_reading[3] < 0.09 or closest_reading[4] < 0.09:
            self._fitness += 5
            return self._states.index("RIGHT")
        elif closest_reading[5] < 0.09:
            self._fitness += 5
            return self._states.index("BEHIND")
        else:
            self._fitness += 10
            return self._states.index("EXPLORE")

    def callback(self):
        self._state = self.get_next_state()

    def save(self):
        pass

    def get_score(self):
        return self._fitness
