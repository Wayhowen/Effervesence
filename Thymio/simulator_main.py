import os

from simulator.behaviors.avoider import Avoider
from simulator.robot_model.controller import Controller
from simulator import Simulator


class Main:
    def __init__(self, number_of_robots=1, frequency_of_saves=50):
        self._delete_previous_records()

        self._number_of_robots = number_of_robots
        self._frequency_of_saves = frequency_of_saves

        self.simulator = Simulator()
        self.robots = [
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H)),
            Avoider(self.simulator, Controller(self.simulator.W, self.simulator.H, 0, 0.5, 2))
        ]

        # used for speed measurment
        self.distances = []

    def _delete_previous_records(self):
        dir_name = "animator/"
        test = os.listdir(dir_name)
        for item in test:
            if item.endswith(".dat"):
                os.remove(os.path.join(dir_name, item))

    def step(self, step: int):
        for robot in self.robots:
            self.simulator.step(robot.controller)
            self.perform(step)
        if cnt % self._frequency_of_saves == 0:
            main.save_positions()

    def perform(self, step: int):
        robots = self.robots[:self._number_of_robots]
        for robot in robots:
            robot.perform(step)

    def save_positions(self):
        robots = self.robots[:self._number_of_robots]
        for index, robot in enumerate(robots):
            with open(f"animator/trajectory_{index}.dat", "a") as file:
                file.write(robot.position)


if __name__ == '__main__':
    main = Main(number_of_robots=2, frequency_of_saves=50)
    for cnt in range(5000):
        # simple single-ray sensor
        try:
            # step simulation
            main.step(cnt)

        except AttributeError:
            main.save_positions()
            print("out of bounds")
            break
