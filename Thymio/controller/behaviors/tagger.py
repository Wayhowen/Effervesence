#!/usr/bin/python3
import random
from typing import Optional, Dict

import numpy as np

from controller.behaviors.behavior import Behavior


class Tagger(Behavior):
    def __init__(self, safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed):
        super().__init__(safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed)
        self.states = (
            "AllFRONT", "INFRONT", "LEFT", "RIGHT", "LEFTFRONT",
            "RIGHTFRONT", "LEFTRIGHT", "NOTHING", "BEHIND"
        )
        self.state = self.states.index("NOTHING")
        self.actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "RANDOM", "LEAN_LEFT", "LEAN_RIGHT", "SLOW_FORWARDS_LEFT",
            "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS"
        )
        self.q_table = np.array([[  7.57721796,   7.57721796,  -3.25910776,  -1.20982259,
         -3.12011823, -15.88580319,  -3.56932733,  -0.58697487,
          7.57721796],
       [ 17.36960666,   1.40779578,   7.16809468,  12.04310912,
          0.91266769, -13.03920876,  14.93839489,  16.78919572,
          8.24674813],
       [  7.57721796,   7.57721796,   7.57721796, -13.65074803,
         -1.93892875,  -5.78162467,  -3.69753777,   1.34185808,
          2.6392372 ],
       [  7.57721796,   7.57721796,   3.54519478, -11.68858698,
        -13.68173249,  -3.99931209,   6.82349099,   7.57721796,
          7.57721796],
       [  7.57721796,   7.57721796,  -8.26299228,  -2.14778526,
          7.57721796, -12.06664052,   0.95340262,   5.95320416,
         12.37354091],
       [  9.6005366 ,  -4.46416056,   7.57721796,   6.01119972,
         10.22730673, -15.64242658,   2.95564354,  -8.71897764,
          1.03666878],
       [  1.5526293 ,   7.57721796,  -4.16117815,   6.11462049,
          7.57721796,  -2.1071922 ,  -5.68443954,  12.10236683,
        -17.1587734 ],
       [  4.51025985,   7.57721796,   7.57721796,  -8.44201904,
         15.90791517,   7.57721796,  -2.84356647,   9.06266343,
         -1.4699734 ],
       [ 10.06469994,  -7.34888093,   9.35453572,  -6.85002791,
         -9.19300134,   7.57721796,   7.57721796, -10.68929462,
         10.2516297 ]])

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

    # TODO: work on this
    def get_next_state(self, closest_reading, other_robot_camera_positions: Dict[str, str]):
        if all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "blue" for k in ["l","m","r"]):
                return self.states.index("ALLFRONT")
        elif all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "blue" for k in ["l","m"]):
            return self.states.index("LEFTFRONT")
        elif all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "blue" for k in ["m","r"]):
            return self.states.index("RIGHTFRONT")
        elif all(other_robot_camera_positions[k] and not other_robot_camera_positions[k] == "blue" for k in ["l","r"]):
            return self.states.index("LEFTRIGHT")
        elif other_robot_camera_positions["m"] and not other_robot_camera_positions["m"] == "blue":
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
            self.perform(cnt)
