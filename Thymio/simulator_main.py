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
        qt = np.array([[3.20342254, -16.37317672, 13.59960545, 9.74758426,
                        -19.30343924, -18.41360453, 5.5396418, 8.41967501,
                        12.63592137],
                       [-10.23114114, 16.19414529, -18.32732052, -13.70467405,
                        -4.23253959, 19.85631537, -13.27068351, -7.91753558,
                        -16.81289398],
                       [-4.00586003, 6.82292354, -12.59196382, 16.44664645,
                        -10.51370024, 3.71086382, 14.21279338, -19.9461394,
                        -9.99208931],
                       [11.72646681, 15.77024078, 8.23435543, 15.201367,
                        -19.2997003, 11.23330677, -15.6593084, -7.0433514,
                        12.24802872],
                       [6.58359833, 5.00650055, -7.52697661, -15.18870747,
                        -11.33587641, 14.27882811, 9.13841063, -6.70622477,
                        15.523229],
                       [8.49690609, -4.05363245, 11.8585629, 8.51626591,
                        -8.52824901, 17.46323311, 19.79412229, 18.86132478,
                        -10.66442267],
                       [14.43052533, 8.79910625, 4.97818434, -2.90524341,
                        -9.56832612, 6.73869809, -17.8606673, -5.14682446,
                        6.20253632]])

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
