#!/usr/bin/python3
import random
import time
from typing import Optional, Dict

import numpy as np

from controller.behaviors.behavior import Behavior


class Tagger(Behavior):
    def __init__(self, safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed):
        super().__init__(safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed)
        self.states = (
            "ALLFRONT", "INFRONT", "LEFT", "RIGHT", "LEFTFRONT",
            "RIGHTFRONT", "LEFTRIGHT", "NOTHING", "BEHIND"
        )
        self.state = self.states.index("NOTHING")
        self.actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "RANDOM", "LEAN_LEFT", "LEAN_RIGHT", "SLOW_FORWARDS_LEFT",
            "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS"
        )
        self.q_table = np.array([[ -8.66586572,   3.7254329 ,  -1.01152472,   3.36527789,
         -5.93302099,  10.23454108,   0.67537878,  -7.68405758,
         -3.59846988],
       [ 14.54002728,   3.7967187 ,  -9.04640878,   2.94561934,
         11.12722187,  13.44035413,  -5.03976046,  13.56795349,
          6.64607533],
       [ -8.83147839,  -5.4888845 ,   4.80560626, -12.2428724 ,
         -1.27577391,  12.00936326,   5.31984367,  -8.49638036,
          2.78911886],
       [-10.64498205,   5.54101129,  12.35902758,   9.81921807,
         -9.39915688,   7.39881322,  -1.57174841,  -2.87986991,
          4.06374859],
       [ 10.55930612, -15.02611793,   0.51928539,  -0.65215661,
         -6.59272714,  -1.80352688,   1.25786735,  -4.60442393,
         -4.78485165],
       [ -4.81029028,  -3.11733687,   3.22068461,  -2.98618893,
         -6.99876894,  -7.26739292,  -3.20777062,   3.35074201,
          1.73398616],
       [  4.53609479,  -2.82276954,   2.63931984, -16.77931002,
         -0.33267119,  -7.38859289, -15.05823261,   8.69618874,
         -8.66739136],
       [ -3.23562762,   2.46579577,   4.36802133,  -6.66081027,
          4.03653471,  13.78519945,   2.61216563, -10.96861865,
         -5.18965933],
       [ -1.28376143,  -0.45539217,   7.29767489,   3.99179954,
         -9.48354564,  -7.97985652,  -2.30501724,  12.99396709,
          5.74439784]])

        self._colors = {
            "seeking": self.controller.light_red,
            "safe_seeking": self.controller.light_orange,
        }
        self._color = self._choose_color("safe_seeking")

        self.controller.start_tagging_other()

    def behavior_specific_set_behaviors(self, _) -> Optional[int]:
        # actions not taking a lot of time
        if self.controller.in_the_safezone() and self._color != "safe_seeking":
            self._choose_color("safe_seeking")
        elif self._color != "seeking":
            self._choose_color("seeking")
        return None

    def behavior_type(self):
        return "Tagger"

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(self.max_speed*2, self.max_speed*2)
        elif action == 1:
            self.controller.drive(-self.half_speed, self.half_speed)
        elif action == 2:
            self.controller.drive(self.half_speed, -self.half_speed)
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

    # TODO: work on this
    def get_next_state(self, closest_reading, other_robot_camera_positions: Dict[str, str]):
        if all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "Purple" for k in ["l","m","r"]):
                return self.states.index("ALLFRONT")
        elif all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "Purple" for k in ["l","m"]):
            return self.states.index("LEFTFRONT")
        elif all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "Purple" for k in ["m","r"]):
            return self.states.index("RIGHTFRONT")
        elif all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "Purple" for k in ["l","r"]):
            return self.states.index("LEFTRIGHT")
        elif other_robot_camera_positions["m"] and not other_robot_camera_positions["m"] == "Purple":
            return self.states.index("INFRONT")
        elif other_robot_camera_positions["l"] and not other_robot_camera_positions["l"] == "Purple":
            return self.states.index("LEFT")
        elif other_robot_camera_positions["r"] and not other_robot_camera_positions["r"] == "Purple":
            return self.states.index("RIGHT")
        elif closest_reading[5] >= self.nine_cm_reading:
            return self.states.index("BEHIND")
        else:
            return self.states.index("NOTHING")

    def run(self, steps=1800):
        for cnt in range(steps):
            self.perform(cnt)
            self.post_move_calculations()
