import os
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
        qt = np.array([[-13.82723692, -15.16240511, -11.15666042,  19.93517494,
          9.01803669, -18.37555726,   7.92345326,  -9.31812369,
         -7.77664774],
       [  9.98070758,  15.49206228,  -7.99116357,   7.20464336,
          6.4372743 ,  -7.12335705, -16.14436547,  10.0526101 ,
          6.20058461],
       [-18.54561113,  -0.39064918, -15.0821271 ,  -1.02687473,
         10.18119671,  -5.78310746,  19.96602757,   8.76996423,
          3.05115788],
       [-13.60841196,  16.88981154,  -9.63138143,  10.84484909,
         -2.9535608 ,   3.45442849, -13.06023551, -10.41333765,
        -16.37067128],
       [ -5.02625459, -11.26850222,   2.83613019,   7.9125036 ,
        -16.47159417,  18.48240991, -17.27618251, -16.16213957,
          6.06611891],
       [-18.54539783,  -1.04347939,  19.36047308,   4.29254163,
          6.89219056, -17.70559467, -10.19519126,   0.25526873,
         16.16647432],
       [ 17.99425168,  16.6547622 ,   5.47498258,   0.59281684,
         10.11465738,  -2.34801744,  16.75501476, -13.87101205,
          1.73595421]])

        w = self.simulator.W - 0.1
        h = self.simulator.H - 0.1
        self.robots: List[Behavior] = [
            # RotationMeasurment(self.simulator,  Controller(self.simulator.W, self.simulator.H, 0, 0, 0))
            TaggerMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, 0, 0), qt,
                            self.number_of_steps),
            # QAvoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, w / 2, h / 2, 4)),
            # # Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, w / 2, -h / 2, 2.5)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, -w / 2, -h / 2, 1)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, -w / 2, h / 2, 5.2))
        ]

        # used for speed measurment
        self.distances = []

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
                print(e)
                break
            if all(robot.is_tagged for robot in self.robots):
                if save_data:
                    self.save_positions()
                break
        if save_data:
            self.save_behavioral_data()

    # this is to be used as the evaluator
    def eval(self, maximizer):
        self.robots[0] = maximizer

        self.run(False)

        return self.robots[0].get_score()


if __name__ == '__main__':
    main = Main(number_of_robots=5, frequency_of_saves=10, number_of_steps=1800)
    # main.save_positions()
    main.run()
