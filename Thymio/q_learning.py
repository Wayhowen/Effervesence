import random

import numpy as np


class QLearner:
    def __init__(self, states, actions, initial_state):
        self.state = initial_state

        self.q_table = np.zeros((len(states), len(actions)))
        self.epsilon = 0.2
        self.learning_rate = 0.1  # between 0 and 1 / alpha
        self.discount_factor = 0.6  # between 0 and 1 / gamma

    def learn(self, step_function):
        if random.uniform(0, 1) < self.epsilon:
            """
            Explore: select a random action
            """
            action = actions[random.randint(0, len(actions))]
        else:
            """
            Exploit: select the action with max value (future reward)
            """
            action = np.argmax(self.q_table[self.state])

        next_state, reward = step_function(action)

        old_value = self.q_table[self.state, action]
        next_max = np.max(self.q_table[next_state])
        self.q_table[self.state, action] = self.update_rule(old_value, next_max)

        self.state = next_state

    def update_rule(self, old_value, next_max):
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
