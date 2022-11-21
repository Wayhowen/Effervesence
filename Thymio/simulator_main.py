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
        qt = np.array([[18.39717329, 5.00042692, 18.30563998, -3.28465326,
                        -1.68126104, -10.137321, -3.63680958, 11.51952344,
                        19.65822753],
                       [11.23349227, -10.31091992, 16.46940038, -6.50086801,
                        -17.01559366, -3.38967495, -12.61541562, 5.73256326,
                        -18.33797779],
                       [13.80909587, 14.33973272, 4.33629855, 3.01366966,
                        5.33179812, -13.84945073, 19.65366288, 7.47190569,
                        4.9032524],
                       [-12.53634257, 17.93428217, -14.39817502, 12.21248594,
                        -3.74115265, 10.70019071, -15.12394064, 3.58940531,
                        -4.17830953],
                       [-2.83251637, -3.05800088, 0.51763708, 7.19794806,
                        3.85013592, -6.36958554, 16.33577905, 1.9585074,
                        2.30315766],
                       [-1.45926686, 8.30789739, 5.91917917, 12.62833243,
                        4.14478838, 10.99865046, -11.17566391, 15.98951575,
                        19.05511264],
                       [-6.65666497, -9.4025922, 9.48806666, -7.10355178,
                        2.11389109, -6.31029848, 3.76194692, 8.92513086,
                        4.34583264]])

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
