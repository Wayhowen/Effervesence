from typing import Dict, Optional

import numpy as np

from controller.behaviors.behavior import Behavior
from controller.controller import Controller


class Avoider(Behavior):
    def __init__(self, safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed):
        super().__init__(safezone_reading, line_reading, five_cm_reading, nine_cm_reading, max_speed)
        self.states = ("INFRONT", "LEFT", "RIGHT", "NOTHING", "BEHIND", "SAFE")
        self.state = self.states.index("NOTHING")
        self.actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "SLOW_BACKWARDS_LEFT", "SLOW_BACKWARDS_RIGHT", "LEAN_LEFT",
            "LEAN_RIGHT", "SLOW_FORWARDS_LEFT", "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS", "STOP"
        )
        # TODO: This is tagger array for now
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

        # add coroutine to set tagged color
        self._colors = {
            "avoiding": self.controller.light_red,
            "safe_avoiding": self.controller.light_orange,
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
        else:
            self._choose_color("safe_avoiding")
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
