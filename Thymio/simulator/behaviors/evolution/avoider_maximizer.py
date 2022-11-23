from typing import Dict

import numpy as np

from simulator.behaviors.behavior import Behavior


class AvoiderMaximizer(Behavior):
    def __init__(self, simulator, controller, q_table, total_steps):
        super().__init__(simulator, controller)
        self._states = ("INFRONT", "LEFT", "RIGHT", "NOTHING", "LINE", "BEHIND", "SAFE")
        self._actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "SLOW_BACKWARDS_LEFT", "SLOW_BACKWARDS_RIGHT", "LEAN_LEFT",
            "LEAN_RIGHT", "SLOW_FORWARDS_LEFT", "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS", "STOP"
        )

        self._q_table = q_table
        self._total_steps = total_steps
        self._state = self._states.index("EXPLORE")
        self._fitness = 1
        self._color = self._colors["avoiding"]
        self._bad_behavior_penalty = 1

    def perform(self, step, other_controllers):
        action = np.argmax(self._q_table[self._state])
        self.perform_next_action(action)

    def _choose_color(self):
        if self.is_in_safezone:
            self._color = self._colors["safe_avoiding"]
            return
        elif self.is_tagged:
            self._color = self._colors["tagged"]

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(7.41, 7.41)
        elif action == 1:
            self.controller.drive(-11.976, 11.976)
        elif action == 2:
            self.controller.drive(11.976, -11.976)
        elif action == 3:
            self.controller.drive(-1.85, -3.7)
        elif action == 4:
            self.controller.drive(-3.7, -1.85)
        elif action == 5:
            self.controller.drive(3.7, 7.41)
        elif action == 6:
            self.controller.drive(7.41, 3.7)
        elif action == 7:
            self.controller.drive(1.85, 3.7)
        elif action == 8:
            self.controller.drive(3.7, 1.85)
        elif action == 9:
            self.controller.drive(3.7, 3.7)
        elif action == 10:
            self.controller.drive(0, 0)

    def get_next_state(self, on_line, closest_reading, other_robot_camera_positions: Dict[str, Behavior]):
        if on_line:
            return self._states.index("LINE")
        elif self.is_in_safezone:
            return self._states.index("SAFE")
        elif other_robot_camera_positions["l"]:
            return self._states.index("LEFT")
        elif other_robot_camera_positions["m"]:
            return self._states.index("INFRONT")
        elif other_robot_camera_positions["r"]:
            return self._states.index("RIGHT")
        elif closest_reading[5] < 0.09:
            return self._states.index("BEHIND")
        else:
            return self._states.index("NOTHING")

    def callback(self, step, other_robots):
        distances_to_objects = [self.controller.distances_to_objects(robot.controller.body) for robot in
                                     other_robots]
        closest_reading = min([(x, sum(x)) for x in distances_to_objects], key=lambda reading: reading[1])[0]
        on_line = self.controller.on_the_line(self.simulator.world, self.simulator.bounds)
        other_robot_camera_positions = self.controller.robots_relative_positions_from_camera(
            other_robots
        )
        self._state = self.get_next_state(on_line, closest_reading, other_robot_camera_positions)

        self.manage_rewards(self._state)

    def manage_rewards(self, state: int):
        if state == self._states.index("SAFE"):
            self._fitness += 1
        if not self.is_tagged:
            self._fitness += 1

    def save(self):
        pass

    def get_score(self):
        score = self._fitness
        if self.is_tagged:
            score -= 1000
        return score
