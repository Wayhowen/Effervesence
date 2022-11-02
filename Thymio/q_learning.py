import random
from os.path import exists

import numpy
import numpy as np


class QLearner:
    def __init__(self, states, actions, initial_state):
        self.states = states
        self.actions = actions
        self.state = initial_state

        self.q_table = None
        self.load_q_table()

        self.epsilon = 0.2
        self.learning_rate = 0.1  # between 0 and 1 / alpha
        self.discount_factor = 0.6  # between 0 and 1 / gamma

    def load_q_table(self):
        if exists("table.txt"):
            with open("table.txt", "rb") as file:
                self.q_table = numpy.load(file, allow_pickle=True)
                print(self.q_table)
        else:
            self.q_table = np.zeros((len(self.states), len(self.actions)))

    def save_q_table(self):
        with open("table.txt", "wb") as file:
            numpy.save(file, self.q_table, allow_pickle=True)

    def learn(self, step_function):
        if random.uniform(0, 1) < self.epsilon:
            """
            Explore: select a random action
            """
            action = random.randint(0, len(self.actions) - 1)
        else:
            """
            Exploit: select the action with max value (future reward)
            """
            action = np.argmax(self.q_table[self.state])

        next_state, reward = step_function(action)

        old_value = self.q_table[self.state, action]
        next_max = np.max(self.q_table[next_state])
        self.q_table[self.state, action] = self.update_rule(old_value, next_max, reward)

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
            q_leaner.learn()
