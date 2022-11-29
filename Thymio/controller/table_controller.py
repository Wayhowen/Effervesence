from controller.modules.aseba_handler import AsebaHandler

import numpy as np
from time import sleep


class TableController:
    def __init__(self, actions, states, state, q_table):
        self.actions = actions
        self.states = states
        self.state = state
        self.q_table = q_table

        self._aseba_handler = AsebaHandler()

    def kill(self):
        self._aseba_handler.stop()
        self._aseba_handler.stopAsebamedulla()

    def detect(self):
        distance = self._aseba_handler.get_proximity_sensor_values()
        if distance[2] > 1500:
            print("Something infront")
            return self.states.index("INFRONT")
        elif distance[0] > 1500 or distance[1] > 1500:
            print("Something on left")
            return self.states.index("RIGHT")
        elif distance[3] > 1500 or distance[4] > 1500:
            print("Something on right")
            return self.states.index("LEFT")
        else:
            return self.states.index("EXPLORE")

    def step_function(self, action):
        if action == 0:
            self._aseba_handler.drive(100, 100)
        elif action == 1:
            self._aseba_handler.drive(-200, 200)
        elif action == 2:
            self._aseba_handler.drive(200, -200)

        # time step
        sleep(0.2)

        return self.detect()

    def run(self, steps=1800):
        for cnt in range(steps):
            action = np.argmax(self.q_table[self.state])
            next_state = self.step_function(action)
            self.state = next_state

