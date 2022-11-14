from q_learning.q_learning import QLearner
from simulator.behaviors.behavior import Behavior
from numpy import cos, sin


class Avoider(Behavior):
    def __init__(self, simulator, controller):
        super().__init__(simulator, controller)

        self._states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
        self._actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")
        self._q_leaner = QLearner(self._states, self._actions, self._states.index("EXPLORE"))

        self._last_action = 0

    def perform(self, step, other_controllers):
        action = self._q_leaner.choose_next_action()
        self.perform_next_action(action)

    def perform_next_action(self, action):
        self._last_action = action
        if action == 0:
            self.controller.drive(0.4, 0.4)
        elif action == 1:
            self.controller.drive(-0.8, 0.8)
        else:
            self.controller.drive(0.8, -0.8)

    def get_next_state_and_reward(self):
        distance_to_objects = self.controller.distances_to_wall(self.simulator.world)
        reward = 0

        if self._last_action == 0:
            if distance_to_objects[2] < 0.49:
                reward -= 10
            else:
                reward += 20
        elif self._last_action == 1:
            if distance_to_objects[0] > 0.49 or distance_to_objects[1] > 0.49:
                reward -= 10
            else:
                reward += 10
        else:
            if distance_to_objects[3] > 0.49 or distance_to_objects[4] > 0.49:
                reward -= 10
            else:
                reward += 10

        if distance_to_objects[2] < 0.49:
            return self._states.index("INFRONT"), reward
        elif distance_to_objects[0] < 0.49 or distance_to_objects[1] < 0.49:
            return self._states.index("LEFT"), reward
        elif distance_to_objects[3] < 0.49 or distance_to_objects[4] < 0.49:
            return self._states.index("RIGHT"), reward
        else:
            return self._states.index("EXPLORE"), reward

    def callback(self):
        self._q_leaner.learn(*self.get_next_state_and_reward())

    def save(self):
        self._q_leaner.save_q_table()

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.09}, {sin(self.controller.q) * 0.09}\n"
