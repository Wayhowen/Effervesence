import os
from time import sleep

import numpy as np

from controller.table_controller import TableController

if __name__ == '__main__':
    try:
        states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
        actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")

        qt = np.array([[-18.73459677, 17.85513261, 8.46207369],
                       [-17.48424916, -6.50523308, -16.38204322],
                       [-13.54136792, -18.96175021, 13.49961487],
                       [15.29404797, -1.92375868, 1.4931672]])
        controller = TableController(actions, states, states.index("EXPLORE"), qt)

        for cnt in range(10000):
            controller.exec()

    except:
        print("Stopping robot")
        controller.stop()
        sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")