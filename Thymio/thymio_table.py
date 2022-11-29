import os
from time import sleep

import numpy as np

from controller.table_controller import TableController


def get_tagger_setup():
    states = ("INFRONT", "LEFT", "RIGHT", "NOTHING", "BEHIND")
    actions = (
        "GOFORWARDS", "GOLEFT", "GORIGHT", "RANDOM", "LEAN_LEFT", "LEAN_RIGHT", "SLOW_FORWARDS_LEFT",
        "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS"
    )
    q_table = np.array([[-18.39622168, -7.98813007, 1.33527662, -16.7623304,
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
    default_state = states.index("NOTHING")
    return states, actions, q_table, default_state


if __name__ == '__main__':
    try:
        states, actions, q_table, default_state = get_tagger_setup()
        controller = TableController(actions, states, default_state, q_table)

        controller.run(steps=1800)

    except Exception as e:
        controller.kill()
