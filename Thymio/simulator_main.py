import copy
import os
import traceback
from collections import Counter
from typing import List

from simulator.behaviors.avoider import Avoider
from simulator.behaviors.behavior import Behavior
from simulator.behaviors.evolution.tagger_maximizer import TaggerMaximizer
from simulator.behaviors.q_learning.avoider import Avoider as QAvoider
from simulator.behaviors.rotation_measurment import RotationMeasurment
from simulator.behaviors.speed_measurment import SpeedMeasurment
from simulator.behaviors.tagger import Tagger
from simulator.robot_model.controller import Controller
from simulator import Simulator
import numpy as np


# old best tagger
# np.array([[-2.45092977, -6.19014622, 16.94927604, -19.60146905, 0.59315807],
#                        [4.6914578, -12.38485668, -12.92214886, 1.58434574, -18.1741076],
#                        [12.34233952, 5.20859123, -7.68773129, -6.46921212, 13.78779591],
#                        [15.99217255, 19.17506055, 11.97167978, -10.54686955, 3.63755071],
#                        [14.76471574, -4.34058819, 9.89114613, -8.69996267, -5.87376137],
#                        [5.41238945, 6.49553993, 8.89827301, 17.62363713, 17.82214014]])

# pre penalty tagger
# qt = np.array([[19.12888603, -11.82295373, -17.87955, -3.87860522, -0.42105126],
#                [15.94672799, -7.9881799, -4.00382276, -4.51083292, 11.24873673],
#                [-6.02734289, -2.03169682, 6.77280174, 15.8314774, 16.12398255],
#                [-7.09192555, -5.56741013, -9.56628779, -19.64831182, -13.28238365],
#                [-11.76079298, 17.87103418, 19.16899884, -16.91661053, 12.01456196],
#                [-5.96350917, 2.06111633, -2.50783847, -4.67777431, 15.78099476]])


class Main:
    def __init__(self, number_of_robots=1, frequency_of_saves=50, number_of_steps=1800):
        self._delete_previous_records()

        self._number_of_robots = number_of_robots
        self._frequency_of_saves = frequency_of_saves
        self.number_of_steps = number_of_steps

        self.simulator = Simulator()
        # qt = np.array([[1., 0., 0., 0.],
        #                [0., 0., 1., 0.],
        #                [0., 1., 0., 0.],
        #                [1., 0., 0., 0.],
        #                [0., 0., 0., 1.]])
        # This one we could use for future generations
        qt = np.array([[-18.39622168,  -7.98813007,   1.33527662, -16.7623304 ,
         -1.25806826,  -7.67294367,   2.02490175,   5.86654672,
         15.76081346],
       [ -2.55914533,  10.59513545,  -5.74456466,  11.79953737,
         -4.44529443,   1.19901548,  -7.81497779,   3.69952752,
         15.1749446 ],
       [ -0.08614815,  -8.33813305,   9.05659117,   5.8274651 ,
         -5.07227584,  13.32168184,  -9.89262203, -12.40337217,
         -6.85871112],
       [ -5.43198225,   8.58656425,  -0.49740548,  -2.48752895,
         -0.68999991,   3.05050637,   3.43709043,  -6.20555478,
        -11.06319357],
       [ 12.21282762,  -5.77456683,  -8.16263591,   4.58758243,
         16.13215604, -10.50367914,   8.16699934,   2.51367282,
          8.62164963],
       [-14.96731633,   3.07800442,  -5.31802538,  -4.4475438 ,
         12.55831699,  -8.67629336,  13.16530316,   0.31691875,
         -9.86918747],
       [ 10.78827761,   0.61713685,  17.02510233,   6.03111262,
         -3.9853573 ,  -0.62173293,  15.08684138,  -0.06108088,
          9.93598199]])

        self.w = self.simulator.W - 0.2
        self.h = self.simulator.H - 0.2
        self.robots: List[Behavior] = [
            # RotationMeasurment(self.simulator,  Controller(self.simulator.W, self.simulator.H, 0, 0, 0))
            TaggerMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, 0, 0), qt,
                            self.number_of_steps),
            # QAvoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, self.w / 2, self.h / 2, 4)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, self.w / 2, -self.h / 2, 2.5)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, -self.w / 2, -self.h / 2, 1)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, -self.w / 2, self.h / 2, 5.2))
        ]

        # used for speed measurment
        self.distances = []

    def _reset_robots(self):
        self.robots[1].controller.x = self.w / 2
        self.robots[1].controller.y = self.h / 2
        self.robots[1].controller.q = 4
        self.robots[1].tagged = False

        self.robots[2].controller.x = self.w / 2
        self.robots[2].controller.y = -self.h / 2
        self.robots[2].controller.q = 2.5
        self.robots[2].tagged = False

        self.robots[3].controller.x = -self.w / 2
        self.robots[3].controller.y = -self.h / 2
        self.robots[3].controller.q = 1
        self.robots[3].tagged = False

        self.robots[4].controller.x = -self.w / 2
        self.robots[4].controller.y = self.h / 2
        self.robots[4].controller.q = 5.2
        self.robots[4].tagged = False

    def _delete_previous_records(self):
        dir_name = "animator/"
        test = os.listdir(dir_name)
        for item in test:
            if item.endswith(".dat"):
                os.remove(os.path.join(dir_name, item))

    def step(self, cnt):
        for robot in self.robots:
            robot.step()
        if cnt % self._frequency_of_saves == 0:
            self.save_positions()

    def perform(self, step: int):
        robots = self.robots[:self._number_of_robots]
        for robot in robots:
            robot.perform(step, list(filter(lambda x: robot is not x, robots)))

    def finalize_calculations(self, step):
        robots = self.robots[:self._number_of_robots]
        for robot in robots:
            robot.callback(step, list(filter(lambda x: robot is not x, robots)))

    def save_positions(self):
        robots = self.robots[:self._number_of_robots]
        for index, robot in enumerate(robots):
            with open(f"animator/trajectory_{index + 1}.dat", "a") as file:
                file.write(robot.position + ", " + robot.camera_range + ", " + robot.color + "\n")

    def save_behavioral_data(self):
        for robot in self.robots[:self._number_of_robots]:
            robot.save()

    # for running simulation with predefined controllers
    def run(self, save_data=True):
        self._reset_robots()
        if save_data:
            self.save_positions()
        for cnt in range(self.number_of_steps):
            # simple single-ray sensor
            try:
                # step simulation
                self.perform(cnt)
                self.step(cnt)
                self.finalize_calculations(cnt)
            except AttributeError as e:
                if save_data:
                    self.save_positions()
                    self.save_behavioral_data()
                print("out of bounds on step", cnt)
                traceback.print_exc()
                break
            robots_caught = Counter(list(robot.is_tagged for robot in self.robots[1:]))
            if robots_caught[True] == 4 or \
                    (robots_caught[True] > 3 and any(robot.is_in_safezone for robot in self.robots[1:])):
                if save_data:
                    self.save_positions()
                break
        if save_data:
            self.save_behavioral_data()

    # this is to be used as the evaluator
    def eval(self, maximizer: Behavior, competitive_maximizer: Behavior):
        if isinstance(maximizer, TaggerMaximizer):
            self.robots[0] = maximizer
            if competitive_maximizer:
                self.robots[1] = copy.deepcopy(competitive_maximizer)
                self.robots[2] = copy.deepcopy(competitive_maximizer)
                self.robots[3] = copy.deepcopy(competitive_maximizer)
                self.robots[4] = copy.deepcopy(competitive_maximizer)
        else:
            self.robots[0] = competitive_maximizer
            if competitive_maximizer:
                self.robots[1] = copy.deepcopy(maximizer)
                self.robots[2] = copy.deepcopy(maximizer)
                self.robots[3] = copy.deepcopy(maximizer)
                self.robots[4] = copy.deepcopy(maximizer)

        self.run(False)
        if isinstance(maximizer, TaggerMaximizer):
            return self.robots[0].get_score()
        else:
            return sorted(self.robots[1:], key=lambda robot: robot.get_score(), reverse=True)[0].get_score()


if __name__ == '__main__':
    main = Main(number_of_robots=5, frequency_of_saves=10, number_of_steps=1800)
    # main.save_positions()
    main.run()
