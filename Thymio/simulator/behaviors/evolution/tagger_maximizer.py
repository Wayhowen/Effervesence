import random

import numpy as np

from simulator.behaviors.behavior import Behavior


class TaggerMaximizer(Behavior):
    def __init__(self, simulator, controller, q_table, total_steps):
        super().__init__(simulator, controller)
        self.states = ("INFRONT", "LEFT", "RIGHT", "NOTHING", "LINE", "BEHIND")
        self.actions = ("GOFORWARDS", "GOLEFT", "GORIGHT", "REVERSE", "RANDOM")

        self._q_table = q_table
        self._total_steps = total_steps
        self._state = self.states.index("NOTHING")
        self._fitness = 1
        self._color = self._colors["safe_seeking"]

    def perform(self, step, other_controllers):
        action = np.argmax(self._q_table[self._state])
        self.perform_next_action(action)


    def _choose_color(self):
        if self.is_in_safezone:
            self._color = self._colors["safe_seeking"]
            return
        self._color = self._colors["seeking"]

    def tag_other_robots(self, step, other_controllers):
        for robot in other_controllers:
            distances_to_objects = self.controller.distances_to_objects(robot.controller.body)
            if any(d and d < 0.09 for d in distances_to_objects):
                if self.try_tagging(robot):
                    self._fitness += self._total_steps - step

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(7.41, 7.41)
        elif action == 1:
            self.controller.drive(-11.976, 11.976)
        elif action == 2:
            self.controller.drive(11.976, -11.976)
        elif action == 3:
            self.controller.drive(-7.41, -7.41)
        elif action == 4:
            self.controller.drive(random.uniform(5, 11.976), random.uniform(0.01, 11.976))

    def get_next_state(self, on_line, distances_to_objects, other_robot_positions):
        #Get the closest reading of those returned
        closest_reading = min([(x, sum(x)) for x in distances_to_objects], key=lambda reading: reading[1])[0]

        if on_line:
            return self.states.index("LINE")
        elif closest_reading[2] < 0.09:
            return self.states.index("INFRONT")
        elif closest_reading[0] < 0.09 or closest_reading[1] < 0.09:
            return self.states.index("LEFT")
        elif closest_reading[3] < 0.09 or closest_reading[4] < 0.09:
            return self.states.index("RIGHT")
        elif closest_reading[5] < 0.09:
            return self.states.index("BEHIND")
        else:
            return self.states.index("NOTHING")

    def callback(self, step, other_robots):
        distances_to_objects = [self.controller.distances_to_objects(robot.controller.body) for robot in other_robots]
        on_line = self.controller.on_the_line(self.simulator.world, self.simulator.bounds)
        other_robot_positions = self.controller.robots_relative_positions_from_camera([body.controller.body for body in other_robots])
        self._state = self.get_next_state(on_line, distances_to_objects, other_robot_positions)

        self.tag_other_robots(step, other_robots)

    def save(self):
        pass

    def get_score(self):
        return self._fitness
