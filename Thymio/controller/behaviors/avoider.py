#!/usr/bin/python3
from typing import Dict, Optional

import numpy as np

from controller.behaviors.behavior import Behavior


class Avoider(Behavior):
    def __init__(self, safezone_reading, left_line_reading, right_line_reading, five_cm_reading, nine_cm_reading, max_speed):
        super().__init__(safezone_reading, left_line_reading, right_line_reading, five_cm_reading, nine_cm_reading, max_speed)
        self.states = (
            "ALLFRONT", "INFRONT", "LEFT", "RIGHT", "LEFTFRONT",
            "RIGHTFRONT", "LEFTRIGHT", "NOTHING", "BEHIND", "SAFE"
        )
        self.state = self.states.index("NOTHING")
        self.actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "SLOW_BACKWARDS_LEFT", "SLOW_BACKWARDS_RIGHT", "LEAN_LEFT",
            "LEAN_RIGHT", "SLOW_FORWARDS_LEFT", "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS", "STOP"
        )
        # TODO: This is tagger array for now
        self.q_table = np.array([[-12.12399769,  1.94152384, -10.74795309,   1.760338  ,
         -9.69986855,  -4.34902464, -16.84931433,  -8.2606792 ,
        -16.84931433,  -5.03854947, -16.84931433],
       [-16.84931433,   15.43520726, -16.84931433,  10.28489694,
          0.8682506 , -16.84931433,  13.99210338, -16.84931433,
          4.9394937 ,  -8.85083745,  -1.53002829],
       [-16.84931433,  -8.40953178,  12.29826124,   7.73609464,
          0.84862718,  -1.18700081,   0.81647818, -10.14919377,
        -13.19371533, -16.84931433,   2.80145806],
       [ -0.3097111 , 17.94938665,  -9.27726556,  -0.54473961,
        -16.84931433, -14.6978903 ,  -0.84065093,   3.53946908,
          6.19448172, -11.71418765,  11.233055  ],
       [-10.72025642, -16.84931433,   8.12604575,   2.50204336,
        -16.84931433,  -1.99112138,  -2.41521913,  -9.35769586,
         -4.31030397,  -2.27613754,  -8.06977402],
       [-16.84931433,   7.42204811,  -5.1272999 ,   6.76504992,
         6.14682342,  -4.74001002,   2.23161508,   6.0814102 ,
        -16.84931433, -16.84931433,  -3.60210247],
       [ -6.73148648, 16.84931433, -16.84931433, -16.84931433,
        -16.84931433, -11.54676809, -16.84931433,   6.29700865,
         12.78370018,  -8.49556063, -16.84931433],
       [  17.13332175, -16.84931433,   3.93901537, -15.08884795,
         10.44464891, 15.209305  , -12.32230116, -16.84931433,
         13.84206515,  11.99334823,   4.95330837],
       [  12.25333667,  -4.29747175, -16.84931433, -16.84931433,
        -17.0758479 ,  -0.17062313,   6.09870713, -13.64187179,
          8.31604076, -11.85754128,   8.76127768],
       [ -0.17480214, -16.84931433,   0.21753683, -11.29972539,
        -14.99829593, -16.84931433, -16.84931433,   3.18049076,
        -16.84931433,   2.35860108,  12.17613239]])

        # add coroutine to set tagged color
        self._colors = {
            "avoiding": self.controller.light_blue,
            "safe_avoiding": self.controller.light_green,
            "tagged": self.controller.light_purple
        }
        self._color = self._choose_color("avoiding")

        self.controller.start_forcing_others_out_of_safezone()

    def behavior_specific_set_behaviors(self, step) -> Optional[int]:
        how_long_ago = float('inf')
        if self.forced_out_of_safezone != 0:
            self._choose_color("avoiding")
            how_long_ago = (step - self.forced_out_of_safezone)
        elif self.controller.in_the_safezone():
            self._choose_color("safe_avoiding")
            self.controller.start_transmitting_bs()
            return self.actions.index("STOP")
        else:
            self._choose_color("avoiding")
            self.controller.start_forcing_others_out_of_safezone()
        if how_long_ago <= self._safezone_out_steps:
            self.controller.start_transmitting_bs()

        # move out of safezone
        if how_long_ago <= self._safezone_forward_steps:
            return self.actions.index("GOFORWARDS")
        elif how_long_ago > self._safezone_forward_steps:
            self.controller.reset_reading()
            self.forced_out_of_safezone = 0
            self.controller.start_forcing_others_out_of_safezone()
        return None

    def behavior_type(self):
        return "Avoider"

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(self.max_speed, self.max_speed)
        elif action == 1:
            self.controller.drive(-self.quarter_speed, self.quarter_speed)
        elif action == 2:
            self.controller.drive(self.quarter_speed, -self.quarter_speed)
        elif action == 3:
            self.controller.drive(-self.quarter_speed, -self.half_speed)
        elif action == 4:
            self.controller.drive(-self.half_speed, -self.quarter_speed)
        elif action == 5:
            self.controller.drive(self.three_quarters_speed, self.max_speed)
        elif action == 6:
            self.controller.drive(self.max_speed, self.three_quarters_speed)
        elif action == 7:
            self.controller.drive(self.quarter_speed, self.half_speed)
        elif action == 8:
            self.controller.drive(self.half_speed, self.quarter_speed)
        elif action == 9:
            self.controller.drive(self.half_speed, self.half_speed)
        elif action == 10:
            self.controller.drive(0, 0)

    # TODO: discuss with Osmanito
    def get_next_state(self, closest_reading, other_robot_camera_positions: Dict[str, str]):
        if self.controller.in_the_safezone():
            return self.states.index("SAFE")
        elif all(other_robot_camera_positions[k] and other_robot_camera_positions[k] in ["seeking", "safe_seeking"] for k in ["l","m","r"]):
            return self.states.index("ALLFRONT")
        elif all(other_robot_camera_positions[k] and other_robot_camera_positions[k] in ["seeking", "safe_seeking"] for k in ["l","m"]):
            return self.states.index("LEFTFRONT")
        elif all(other_robot_camera_positions[k] and other_robot_camera_positions[k] in ["seeking", "safe_seeking"] for k in ["m","r"]):
            return self.states.index("RIGHTFRONT")
        elif all(other_robot_camera_positions[k] and other_robot_camera_positions[k] in ["seeking", "safe_seeking"] for k in ["l","r"]):
            return self.states.index("LEFTRIGHT")
        elif other_robot_camera_positions["l"] and other_robot_camera_positions["l"] in ["seeking", "safe_seeking"]:
            return self.states.index("LEFT")
        elif other_robot_camera_positions["m"] and other_robot_camera_positions["m"] in ["seeking", "safe_seeking"]:
            return self.states.index("INFRONT")
        elif other_robot_camera_positions["r"] and other_robot_camera_positions["r"] in ["seeking", "safe_seeking"]:
            return self.states.index("RIGHT")
        elif closest_reading[5] < 0.09:
            return self.states.index("BEHIND")
        else:
            return self.states.index("NOTHING")

    def is_tagged(self) -> bool:
        if not self._alive:
            return True
        return self.controller.receive_information() == 1

    def is_forced_out_of_safezone(self) -> bool:
        return self.controller.receive_information() == 2
