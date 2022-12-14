import random
from os.path import exists

import numpy as np


class QLearner:
    def __init__(self, states, actions, initial_state, q_table=None, epsilon=0.2):
        self.states = states
        self.actions = actions
        self.state = initial_state

        self.q_table = q_table
        if q_table is None:
            self.load_q_table()

        self.epsilon = epsilon
        self.learning_rate = 0.1  # between 0 and 1 / alpha
        self.discount_factor = 0.6  # between 0 and 1 / gamma

        self._current_action = None

    def load_q_table(self):
        if exists("../table.txt"):
            print("Loading Q-Table fro memory")
            with open("../table.txt", "rb") as file:
                self.q_table = np.load(file, allow_pickle=True)
                print(self.q_table)
        else:
            print("Creating new Q-Table")
            self.q_table = np.zeros((len(self.states), len(self.actions)))

    def save_q_table(self):
        with open("../table.txt", "wb") as file:
            np.save(file, self.q_table, allow_pickle=True)

    # learn is split into 2 functions to allow for refactored simulator
    def choose_next_action(self):
        if random.uniform(0, 1) < self.epsilon:
            """
            Explore: select a random action
            """
            self._current_action = random.randint(0, len(self.actions) - 1)
        else:
            """
            Exploit: select the action with max value (future reward)
            """
            self._current_action = np.argmax(self.q_table[self.state])
        return self._current_action

    # this has to be called after action chosen -> step performed -> then this
    def learn(self, next_state, reward):
        old_value = self.q_table[self.state, self._current_action]
        next_max = np.max(self.q_table[next_state])
        self.q_table[self.state, self._current_action] = self.update_rule(old_value, next_max, reward)

        self.state = next_state

    def update_rule(self, old_value, next_max, reward):
        return (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)


if __name__ == '__main__':
    states = ("TOO FAR", "TOO CLOSE", "PERFECT")
    actions = ("FORWARDS", "BACKWARDS", "STOP")
    q_leaner = QLearner(states, actions, "PERFECT")

    for i in range(1, 100001):
        epochs, penalties, reward, = 0, 0, 0
        done = False

        while not done:
            q_leaner.choose_next_action()
