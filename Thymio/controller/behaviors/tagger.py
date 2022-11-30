import random
from typing import Optional, Dict

import numpy as np

from controller.controller import Controller


class Tagger:
    def __init__(self, safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed):
        self.controller = Controller(safezone_reading, line_reading)
        self.five_cm_reading = five_cm_reading
        self.nine_cm_reading = nine_cm_reading
        self.max_speed = max_speed
        self.half_speed = max_speed / 2
        self.quarter_speed = max_speed / 4
        self.states = ("INFRONT", "LEFT", "RIGHT", "NOTHING", "BEHIND")
        self.state = self.states.index("NOTHING")
        self.actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "RANDOM", "LEAN_LEFT", "LEAN_RIGHT", "SLOW_FORWARDS_LEFT",
            "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS"
        )
        self.q_table = np.array([[-18.39622168, -7.98813007, 1.33527662, -16.7623304,
                                  -1.25806826, -7.67294367, 2.02490175, 5.86654672,
                                  15.76081346],
                                 [-2.55914533, 10.59513545, -5.74456466, 11.79953737,
                                  -4.44529443, 1.19901548, -7.81497779, 3.69952752,
                                  15.1749446],
                                 [-0.08614815, -8.33813305, 9.05659117, 5.8274651,
                                  -5.07227584, 13.32168184, -9.89262203, -12.40337217,
                                  -6.85871112],
                                 [-5.43198225, 8.58656425, -0.49740548, -2.48752895,
                                  -0.68999991, 3.05050637, 3.43709043, -6.20555478,
                                  -11.06319357],
                                 [12.21282762, -5.77456683, -8.16263591, 4.58758243,
                                  16.13215604, -10.50367914, 8.16699934, 2.51367282,
                                  8.62164963],
                                 [-14.96731633, 3.07800442, -5.31802538, -4.4475438,
                                  12.55831699, -8.67629336, 13.16530316, 0.31691875,
                                  -9.86918747],
                                 [10.78827761, 0.61713685, 17.02510233, 6.03111262,
                                  -3.9853573, -0.62173293, 15.08684138, -0.06108088,
                                  9.93598199]])

        self._colors = {
            "seeking": self.controller.light_red,
            "safe_seeking": self.controller.light_orange,
        }
        self._color = self._choose_color("safe_seeking")

        self._sleepy_time = 0.1  # same as in simulator
        self._avoidance_steps_left = 0
        self._avoidance_action = None
        self.last_closest_readings = [float('inf')] * 7

        self.controller.start_tagging_other()

    def _choose_color(self, color: str):
        self._colors[color]()
        return color

    def perform(self):
        action = self.check_set_behaviors()
        if action:
            self.perform_next_action(action)
            return
        action = np.argmax(self.q_table[self.state])
        self.perform_next_action(action)

    def check_set_behaviors(self):
        behavior_specific_action = self.behavior_specific_set_behaviors()
        if behavior_specific_action:
            return behavior_specific_action
        return self.common_set_behaviors()

    def behavior_specific_set_behaviors(self) -> Optional[int]:
        # actions not taking a lot of time
        if self.controller.in_the_safezone() and self._color != "safe_seeking":
            self._choose_color("safe_seeking")
        elif self._color != "seeking":
            self._choose_color("safe_seeking")
        return None

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

    # TODO: adjust speeds
    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(self.max_speed, self.max_speed)
        elif action == 1:
            self.controller.drive(-self.max_speed, self.max_speed)
        elif action == 2:
            self.controller.drive(self.max_speed, -self.max_speed)
        elif action == 3:
            self.controller.drive(
                random.uniform(self.quarter_speed, self.max_speed),
                random.uniform(self.quarter_speed, self.max_speed)
            )
        elif action == 4:
            self.controller.drive(self.half_speed, self.max_speed)
        elif action == 5:
            self.controller.drive(self.max_speed, self.half_speed)
        elif action == 6:
            self.controller.drive(self.quarter_speed, self.half_speed)
        elif action == 7:
            self.controller.drive(self.half_speed, self.quarter_speed)
        elif action == 8:
            self.controller.drive(self.half_speed, self.half_speed)

    def post_move_calculations(self, step):
        self.last_closest_readings = self.controller.get_proximity_sensor_values()
        # TODO: add this
        other_robot_camera_positions = {}
        self._state = self.get_next_state(self.last_closest_readings, other_robot_camera_positions)

    # TODO: work on this
    def get_next_state(self, closest_reading, other_robot_camera_positions: Dict[str, str]):
        if other_robot_camera_positions["m"] and not other_robot_camera_positions["m"] == "blue":
            return self.states.index("INFRONT")
        elif other_robot_camera_positions["l"] and not other_robot_camera_positions["l"] == "blue":
            return self.states.index("LEFT")
        elif other_robot_camera_positions["r"] and not other_robot_camera_positions["r"] == "blue":
            return self.states.index("RIGHT")
        elif closest_reading[5] >= self.nine_cm_reading:
            return self.states.index("BEHIND")
        else:
            return self.states.index("NOTHING")

    def run(self, steps=1800):
        for cnt in range(steps):
            self.perform()

    def kill(self):
        self.controller.kill()