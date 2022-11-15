import numpy as np


class Chromosome:
    def __init__(self, q_table=None, x=5, y=4):
        self.q_table = q_table
        if q_table is None:
            self.q_table = np.random.uniform(-20, 20, (x, y))

    def get_table(self):
        return self.q_table
