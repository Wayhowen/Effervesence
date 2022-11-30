#!/usr/bin/python3
from abc import abstractmethod
from typing import Optional, Dict

import numpy as np

from controller.controller import Controller


class Behavior:
    def __init__(self, safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed):
        self.controller = Controller(safezone_reading, line_reading)
        self.five_cm_reading = five_cm_reading
        self.nine_cm_reading = nine_cm_reading
        self.max_speed = max_speed
        self.half_speed = max_speed / 2
        self.quarter_speed = max_speed / 4

        self._sleepy_time = 0.1  # same as in simulator
        self._avoidance_steps_left = 0
        self._avoidance_action = None
        self.last_closest_readings = [float('inf')] * 7

        # to be declared on inheriting classes
        self.states = ()
        self.state = None
        self.actions = ()
        self.q_table = np.array([[]])
        self._colors = {}
        self._color = None

    def _choose_color(self, color: str):
        self._colors[color]()
        return color

    def perform(self, step):
        action = self.check_set_behaviors(step)
        if action:
            self.perform_next_action(action)
            return
        action = np.argmax(self.q_table[self.state])
        self.perform_next_action(action)

    def check_set_behaviors(self, step):
        behavior_specific_action = self.behavior_specific_set_behaviors(step)
        if behavior_specific_action:
            return behavior_specific_action
        return self.common_set_behaviors()

    @abstractmethod
    def behavior_specific_set_behaviors(self, step) -> Optional[int]:
        pass

    def common_set_behaviors(self) -> Optional[int]:
        # line turn behavior
        left_on_line, right_on_line = self.controller.on_the_line()
        if right_on_line:
            return self.actions.index("GOLEFT")
        elif left_on_line:
            return self.actions.index("GORIGHT")
        # avoidance behavior -- basically turn for a bit
        if self._avoidance_steps_left:
            self._avoidance_steps_left -= 1
            return self._avoidance_action
        if self.last_closest_readings:
            if self.last_closest_readings[4] >= self.five_cm_reading:
                self._avoidance_steps_left = 4
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[3] >= self.five_cm_reading:
                self._avoidance_steps_left = 5
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[2] >= self.five_cm_reading:
                self._avoidance_steps_left = 6
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[1] >= self.five_cm_reading:
                self._avoidance_steps_left = 7
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[0] >= self.five_cm_reading:
                self._avoidance_steps_left = 8
                # this has to use action that we have set on both controllers
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
        return None

    @abstractmethod
    def perform_next_action(self, action):
        pass

    def post_move_calculations(self):
        self.last_closest_readings = self.controller.get_proximity_sensor_values()
        other_robot_camera_positions = {}
        self._state = self.get_next_state(self.last_closest_readings, other_robot_camera_positions)

    @abstractmethod
    def get_next_state(self, closest_readings, other_robot_camera_positions: Dict[str, str]):
        pass

    def run(self, steps=1800):
        for cnt in range(steps):
            self.perform(cnt)

    def kill(self):
        self.controller.kill()