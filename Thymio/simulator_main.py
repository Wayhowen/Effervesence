import os
from typing import List

from simulator.behaviors.avoider import Avoider
from simulator.behaviors.behavior import Behavior
from simulator.behaviors.evolution.tagger_maximizer import TaggerMaximizer
from simulator.behaviors.q_learning.avoider import Avoider as QAvoider
from simulator.behaviors.tagger import Tagger
from simulator.robot_model.controller import Controller
from simulator import Simulator
import numpy as np


class Main:
    def __init__(self, number_of_robots=1, frequency_of_saves=50, number_of_steps=10000):
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
        qt = np.array([[2.6912336, -8.05926428, -9.88683191, -13.91666527],
                       [11.53264843, 9.38577946, -10.92145655, 0.02460526],
                       [-1.72789116, 14.65135718, -15.06050577, 5.63157866],
                       [5.67430883, 0.59958208, 2.77673922, -13.2959877],
                       [-1.70007198, -3.61565218, 9.77073823, 17.41248385],
                       [-14.17177669, -6.72203539, 1.10478413, -14.43229334]])

        w = self.simulator.W - 0.1
        h = self.simulator.H - 0.1
        self.robots: List[Behavior] = [
            TaggerMaximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, 0, 0), qt, self.number_of_steps),
            # QAvoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, w / 2, h / 2, 4)),
            # Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
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

    def finalize_calculations(self):
        for robot in self.robots[:self._number_of_robots]:
            robot.callback()

    def save_positions(self):
        robots = self.robots[:self._number_of_robots]
        for index, robot in enumerate(robots):
            with open(f"animator/trajectory_{index + 1}.dat", "a") as file:
                file.write(robot.position)

    def save_behavioral_data(self):
        for robot in self.robots[:self._number_of_robots]:
            robot.save()

    # for running simulation with predefined controllers
    def run(self, save_data=True):
        self.save_positions()
        for cnt in range(self.number_of_steps):
            # simple single-ray sensor
            try:
                # step simulation
                self.perform(cnt)
                self.step(cnt)
                self.finalize_calculations()
            except AttributeError as e:
                self.save_positions()
                self.save_behavioral_data()
                print("out of bounds on step", cnt)
                print(e)
                break
            if all(robot.is_tagged for robot in self.robots):
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
    main = Main(number_of_robots=5, frequency_of_saves=50, number_of_steps=5000)
    main.run()
