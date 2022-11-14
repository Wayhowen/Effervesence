import numpy as np
from shapely.geometry import Point

from simulator.robot_model.controller import Controller
from simulator.simulator import Simulator


class Evaluator:
    def __init__(self):
        self.states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
        self.actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")
        self.simulator = Simulator()
        self.controller = Controller(self.simulator.W, self.simulator.H)
        self.fitness = 1

    def step_function(self, action):
        prox_horizontal = self.controller.distances_to_wall(self.simulator.world)

        if action == 0:
            self.controller.drive(0.4, 0.4)
            self.fitness += 10
        elif action == 1:
            self.controller.drive(-0.8, 0.8)   
        else:
            self.controller.drive(0.8, -0.8)

        # step simulation
        self.simulator.step(self.controller)

        if prox_horizontal[2] < 0.49:
            return self.states.index("INFRONT"), 0
        elif prox_horizontal[0] < 0.49 or prox_horizontal[1] < 0.49:
            return self.states.index("LEFT"), 0
        elif prox_horizontal[3] < 0.49 or prox_horizontal[4] < 0.49:
            return self.states.index("RIGHT"), 0
        else:
            return self.states.index("EXPLORE"), 0
    
    def eval(self, q_table):
        self.simulator = Simulator()
        self.controller = Controller(self.simulator.W, self.simulator.H)
        self.fitness = 1
        state = self.states.index("EXPLORE")

        for cnt in range(10000):
            action = np.argmax(q_table[state])
            next_state, _ = self.step_function(action)
            state = next_state
            # check collision with arena walls
            if self.simulator.world.distance(Point(self.controller.x, self.controller.y)) < self.simulator.L / 2:
                self.fitness += cnt
                break

        return self.fitness/2

"""
sim = Evaluator()
qt = np.array([[3.33097617, 7.73470281, -2.47455146],
                [10.81399647, 9.17409251, -0.88740361], 
                [13.18743587, 7.96218889, 7.54547456],
                [13.38585149, -0.71430643, -0.87117399]])


start = time.time()
print(sim.eval(qt))
end = time.time()
print(end - start)"""
