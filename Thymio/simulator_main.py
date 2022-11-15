import os
from typing import List

from simulator.behaviors.avoider import Avoider
from simulator.behaviors.behavior import Behavior
from simulator.behaviors.evolution.maximizer import Maximizer
from simulator.behaviors.q_learning.avoider import Avoider as QAvoider
from simulator.robot_model.controller import Controller
from simulator import Simulator
import numpy as np

class Main:
    def __init__(self, number_of_robots=1, frequency_of_saves=50):
        self._delete_previous_records()

        self._number_of_robots = number_of_robots
        self._frequency_of_saves = frequency_of_saves

        self.simulator = Simulator()
        qt = np.array([[1., 0., 0., 0.],
                       [0., 1., 0., 0.],
                       [0., 0., 1., 0.],
                       [1., 0., 0., 0.],
                       [0., 0., 0., 1.]])
        self.robots: List[Behavior] = [
            QAvoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            Maximizer(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, 0.5, 2), qt),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, -0.5, 2)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, 0.5, 0, 2)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, -0.5, 0.5, 2))
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
            main.save_positions()

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
            with open(f"animator/trajectory_{index+1}.dat", "a") as file:
                file.write(robot.position)

    def save_behavioral_data(self):
        for robot in self.robots[:self._number_of_robots]:
            robot.save()

    # for running simulation with predefined controllers
    def run(self, steps=10000, save_data=True):
        for cnt in range(steps):
            # simple single-ray sensor
            try:
                # step simulation
                main.perform(cnt)
                main.step(cnt)
                main.finalize_calculations()
            except AttributeError as e:
                main.save_positions()
                main.save_behavioral_data()
                print("out of bounds on step", cnt)
                print(e)
                break
        if save_data:
            main.save_behavioral_data()

    # this is to be used as the evaluator
    def eval(self, q_table, steps=10000):
        self.robots[0] = Maximizer(self.simulator, Controller(self.simulator.W, self.simulator.H), q_table)

        self.run(steps, False)

        return self.robots[0].get_score()


if __name__ == '__main__':
    main = Main(number_of_robots=5, frequency_of_saves=50)
    main.run(10000)
