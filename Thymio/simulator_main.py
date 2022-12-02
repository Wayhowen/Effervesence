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
        tagger_qt = np.array([[ -8.66586572,   3.7254329 ,  -1.01152472,   3.36527789,
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

        avoider_qt = np.array([[-12.12399769,  -0.94152384, -10.74795309,   1.760338  ,
         -9.69986855,  -4.34902464, -16.84931433,  -8.2606792 ,
        -16.84931433,  -5.03854947, -16.84931433],
       [-16.84931433,   2.43520726, -16.84931433,  10.28489694,
          0.8682506 , -16.84931433,  13.99210338, -16.84931433,
          4.9394937 ,  -8.85083745,  -1.53002829],
       [-16.84931433,  -8.40953178,  12.29826124,   7.73609464,
          0.84862718,  -1.18700081,   0.81647818, -10.14919377,
        -13.19371533, -16.84931433,   2.80145806],
       [ -0.3097111 , -17.94938665,  -9.27726556,  -0.54473961,
        -16.84931433, -14.6978903 ,  -0.84065093,   3.53946908,
          6.19448172, -11.71418765,  11.233055  ],
       [-10.72025642, -16.84931433,   8.12604575,   2.50204336,
        -16.84931433,  -1.99112138,  -2.41521913,  -9.35769586,
         -4.31030397,  -2.27613754,  -8.06977402],
       [-16.84931433,   7.42204811,  -5.1272999 ,   6.76504992,
         16.14682342,  -4.74001002,   2.23161508,   6.0814102 ,
        -16.84931433, -16.84931433,  -3.60210247],
       [ -6.73148648, -16.84931433, -16.84931433, -16.84931433,
        -16.84931433, -11.54676809, -16.84931433,   6.29700865,
         12.78370018,  -8.49556063, -16.84931433],
       [  0.13332175, -16.84931433,   3.93901537, -15.08884795,
         10.44464891, 17.209305  , -12.32230116, -16.84931433,
         13.84206515,  11.99334823,   4.95330837],
       [  2.25333667,  -4.29747175, -16.84931433, -16.84931433,
        -17.0758479 ,  -0.17062313,   6.09870713, -13.64187179,
          8.31604076, -11.85754128,   8.76127768],
       [ -0.17480214, -16.84931433,   0.21753683, -11.29972539,
        -14.99829593, -16.84931433, -16.84931433,   3.18049076,
        -16.84931433,   2.35860108,  12.17613239]])

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
