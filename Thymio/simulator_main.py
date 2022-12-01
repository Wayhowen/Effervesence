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
        tagger_qt = np.array([[  7.57721796,   7.57721796,  -3.25910776,  -1.20982259,
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

        avoider_qt = np.array([[  4.70106709,  -5.33667302,  13.6439214 ,  10.9758712 ,
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
