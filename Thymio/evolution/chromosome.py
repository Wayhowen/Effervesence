import numpy as np


class Chromosome:
    def __init__(self, q_table=None):
        self.q_table = q_table
        if q_table is None:
            self.q_table = np.random.uniform(-20, 20, (4, 3))

    def get_table(self):
        return self.q_table
