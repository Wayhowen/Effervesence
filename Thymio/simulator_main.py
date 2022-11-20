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
        qt = np.array([[-2.45092977, -6.19014622, 16.94927604, -19.60146905, 0.59315807],
                       [4.6914578, -12.38485668, -12.92214886, 1.58434574, -18.1741076],
                       [12.34233952, 5.20859123, -7.68773129, -6.46921212, 13.78779591],
                       [15.99217255, 19.17506055, 11.97167978, -10.54686955, 3.63755071],
                       [14.76471574, -4.34058819, 9.89114613, -8.69996267, -5.87376137],
                       [5.41238945, 6.49553993, 8.89827301, 17.62363713, 17.82214014]])

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
                file.write(robot.position+", "+robot.camera_range+", "+robot.color+"\n")

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
                self.finalize_calculations()
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
    #main.save_positions()
    main.run()
