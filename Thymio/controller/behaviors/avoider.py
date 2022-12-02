#!/usr/bin/python3
from typing import Dict, Optional

import numpy as np

from controller.behaviors.behavior import Behavior


class Avoider(Behavior):
    def __init__(self, safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed):
        super().__init__(safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed)
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
        self.q_table = np.array([[  4.70106709,  -5.33667302,  13.6439214 ,  10.9758712 ,
          9.20787715,   3.6445551 ,  13.6439214 ,  13.6439214 ,
          5.77920462, -11.0239956 ,  13.6439214 ],
       [  6.21385072,  -3.57623965,   6.41520309,  -3.78762405,
         -1.75707959,   4.52427251,  13.6439214 ,  15.38178462,
         -4.28120695,  14.79543013,  13.6439214 ],
       [  1.67525629,  -9.77503348,  13.6439214 ,  -0.79279579,
         13.6439214 ,  -2.31381983,   2.43524143,  -3.78762405,
         13.6439214 , -11.39248002,   7.08732981],
       [ 13.6439214 ,   0.13008544,   3.70070875,  -0.81261741,
        -14.03832434,   4.99102294,   8.84767887,   5.63519018,
         -3.78762405,  -3.61941745,   9.01429953],
       [ 12.00348924,  -3.78762405,  13.6439214 ,  -3.78762405,
         13.6439214 ,  13.6439214 ,   0.08644038,  13.6439214 ,
         -5.79065097,  13.6439214 ,   8.54960262],
       [  3.3491366 ,  13.6439214 ,  13.6439214 ,   5.2188861 ,
         13.6439214 ,  -2.13824699, -14.49671495,   4.29960987,
          4.1654641 ,  -7.16516109,  13.6439214 ],
       [ -3.23036316,  11.9122925 ,  -2.75999968, -15.51303004,
         -6.4344585 ,  13.6439214 ,  10.91660862,   6.78290083,
         13.6439214 ,  13.6439214 ,   1.5984953 ],
       [ 13.6439214 ,  -3.04102144,  13.6439214 ,  -3.78762405,
        -12.90135363,  13.6439214 ,  -1.01237154,  13.6439214 ,
         -6.53529709,  13.6439214 ,  13.6439214 ],
       [  9.78086563, -11.88578745,   8.03205226,   4.71607745,
         -2.67092032, -11.61828562,  13.6439214 ,   8.69330604,
         -7.38308518,   4.7470431 ,  -1.32011737],
       [  1.53856321,  -1.94932013,   4.27403389,  13.6439214 ,
          8.74799704,  -3.78762405,  -3.78762405,  15.0242162 ,
          7.61529838,   5.69426831,   2.81185051]])

        # add coroutine to set tagged color
        self._colors = {
            "avoiding": self.controller.light_blue,
            "safe_avoiding": self.controller.light_green,
            "tagged": self.controller.light_purple
        }
        self._color = self._choose_color("avoiding")

        self.forced_out_of_safezone = 0
        self._safezone_out_steps = 50
        self._safezone_forward_steps = 10

        self.controller.start_transmitting_bs()

    def behavior_specific_set_behaviors(self, step) -> Optional[int]:
        how_long_ago = float('inf')
        if self.forced_out_of_safezone != 0:
            self._choose_color("avoiding")
            how_long_ago = (step - self.forced_out_of_safezone)
        elif self.controller.in_the_safezone():
            self._choose_color("safe_avoiding")
            return self.actions.index("STOP")
        else:
            self._choose_color("avoiding")
        if how_long_ago <= self._safezone_out_steps:
            self.controller.start_transmitting_bs()

        # move out of safezone
        if how_long_ago <= self._safezone_forward_steps:
            return self.q_table[self.actions.index("GOFORWARDS")]
        return None

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(self.max_speed, self.max_speed)
        elif action == 1:
            self.controller.drive(-self.max_speed, self.max_speed)
        elif action == 2:
            self.controller.drive(self.max_speed, -self.max_speed)
        elif action == 3:
            self.controller.drive(-self.quarter_speed, -self.half_speed)
        elif action == 4:
            self.controller.drive(-self.half_speed, -self.quarter_speed)
        elif action == 5:
            self.controller.drive(self.half_speed, self.max_speed)
        elif action == 6:
            self.controller.drive(self.max_speed, self.half_speed)
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
