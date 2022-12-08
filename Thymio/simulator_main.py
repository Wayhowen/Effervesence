import copy
import os
import traceback
from collections import Counter
from typing import List

from simulator.behaviors.avoider import Avoider
from simulator.behaviors.behavior import Behavior
from simulator.behaviors.evolution.tagger_maximizer import TaggerMaximizer
from simulator.behaviors.evolution.avoider_maximizer import AvoiderMaximizer
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
        tagger_qt = np.array([[ 18.47831626,   8.14465433, -18.20101289,   5.85490488,
         10.8540814 ,  16.99961007,  -9.03152496,   5.04179577,
         18.59272507],
       [ -0.44686543,  18.16362775,  19.93812208,   5.87407562,
          8.44643258,  -3.36705171,   1.87139086, -19.89454265,
        -17.06400839],
       [ -9.32202419,   0.03816162,  14.30300758,  -6.5834683 ,
         -5.36261776,   8.22254099,  -7.28124644,  -8.48364345,
        -19.32241707],
       [  8.0019731 ,  15.29368626,  17.22088832,   4.4023728 ,
        -16.98810579,  -2.36013228,   1.80510675,   3.5338578 ,
          2.362027  ],
       [ -8.79858469,   5.02951868,  -8.60003142, -12.18567292,
         -2.16332689,   5.15275942,  -8.61257497,  17.42430619,
         10.94303795],
       [ -2.92493238,  17.06600941,  -5.84089018,   7.05124547,
        -12.82365006,   0.19548584,   5.97190655,  -7.80029301,
          8.40184338],
       [ -7.77533111,  -5.87329937,   2.29827983, -17.03810691,
         11.92430471,  -9.32256196,  -2.57914285,  11.28943429,
         16.26933157],
       [ 15.6519265 ,  17.72922986,   2.91637401,  -3.9908131 ,
        -17.73401578,   9.56114149,  15.1650121 , -17.82650359,
        -19.34396531],
       [-16.44431611,  19.34107212,   9.33244754,   3.07336602,
          5.3125196 ,   7.01740778,   1.91177102,  15.9256021 ,
          1.96764109]])

        avoider_qt = np.array([[-10.64338275, -12.63593852,   8.01052149, -12.8889555 ,
         16.17303567,   6.70964014,   8.01052149,   8.01052149,
         -3.29438979,  -0.59083328,   0.84725664],
       [ -2.08499726, -16.76767969,   8.01052149, -15.60740598,
          8.01052149,  14.99991382,   5.32208408,  19.93359079,
         19.79171581,   8.01052149, -16.18826943],
       [  9.55095211,  -5.64248013,  -7.82625758, -18.93292795,
          8.01052149,  10.93631575,  18.82626709,   8.01052149,
          8.01052149,   1.07077875,  -5.86648546],
       [  8.01052149,  -9.21487969, -18.02784463,   6.96214732,
        -15.08873576,  14.45237997,   8.12921353,  15.11937033,
         -6.52947299,  14.89611794,   8.01052149],
       [-16.84509043,  11.60286041,   8.01052149,  10.86763595,
        -15.90370879,  11.88311671,   3.00213422,  18.99329204,
        -13.42801253,   8.01052149, -18.45779761],
       [  8.01052149,   8.01052149, -16.07021815,   8.01052149,
        -10.02375143,  10.05482346, -11.95869404,   6.17486814,
          8.01052149,   8.01052149,  19.0115623 ],
       [-17.30609989,   8.01052149,   8.01052149,  16.52795143,
         -1.92526367,  -9.97027615,   9.95185788,  -3.99681908,
        -18.1464928 , -12.91524624,   8.01052149],
       [ 10.09125645,   8.01052149,   8.01052149,   6.31040215,
        -12.09709478, -12.65452239,   1.20885151,  -6.90253157,
        -14.07854336,  19.32111028,   8.01052149],
       [-14.41986457,  12.0521623 ,   8.01052149,   8.01052149,
          8.01052149,  -3.09287229,  15.30371308,  10.18375747,
          6.55617797,  11.21379371,   8.01052149],
       [ 14.78028902,  -2.34441019, -18.04021627,   8.01052149,
         -4.78940656,   6.95826282,   0.02573428,  -5.49089926,
          8.01052149,  17.83880063,   2.17262365]])

        self.w = self.simulator.W - 0.2
        self.h = self.simulator.H - 0.2
        self.robots: List[Behavior] = [
            # RotationMeasurment(self.simulator,  Controller(self.simulator.W, self.simulator.H, 0, 0, 0))
            TaggerMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, 0, 0), tagger_qt,
                            self.number_of_steps),
            # QAvoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            AvoiderMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, self.w / 2, self.h / 2, 4), avoider_qt, self.number_of_steps),
            AvoiderMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, self.w / 2, -self.h / 2, 2.5), avoider_qt, self.number_of_steps),
            AvoiderMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, -self.w / 2, -self.h / 2, 1), avoider_qt, self.number_of_steps),
            AvoiderMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, -self.w / 2, self.h / 2, 5.2), avoider_qt, self.number_of_steps)
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

    def step(self):
        for robot in self.robots:
            robot.step()

    def perform(self, step: int):
        robots = self.robots[:self._number_of_robots]
        for robot in robots:
            robot.perform(step, list(filter(lambda x: robot is not x, robots)))

    def finalize_calculations(self, step):
        robots = self.robots[:self._number_of_robots]
        for robot in robots:
            robot.callback(step, list(filter(lambda x: robot is not x, robots)))

    def save_positions(self):
        print("saving")
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
                self.step()
                if save_data and cnt % self._frequency_of_saves == 0:
                    self.save_positions()
                self.finalize_calculations(cnt)
            except AttributeError as e:
                if save_data :
                    self.save_positions()
                    self.save_behavioral_data()
                print("out of bounds on step", cnt)
                traceback.print_exc()
                break
            robots_caught = Counter(list(robot.is_tagged for robot in self.robots[1:]))
            if robots_caught[True] == 4 or \
                    (robots_caught[True] >= 3 and any(robot.is_in_safezone for robot in self.robots[1:])):
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
