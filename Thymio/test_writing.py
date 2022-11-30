import threading
import time

import numpy as np

class One:
    def __init__(self):
        self.die = False

    def run(self):
        while not self.die:
            time.sleep(0.5)
        print("died")


class Two:
    def __init__(self):
        pass

    def run(self, c1):
        time.sleep(5)
        c1.die = True
        print("set die")

if __name__ == "__main__":
    # a = np.array([[1, 2], [3, 4]])
    # a = np.array([[5, 6], [7, 8]])
    # with open("test.txt", "ab") as file:
    #     np.save(file, a, False)

    # with open('test.txt', 'rb') as f:
    #     a = np.load(f, allow_pickle=True)
    #     b = np.load(f, allow_pickle=True)
    #     print(a)
    #     print(b)

    one = One()
    two = Two()

    t1 = threading.Thread(target=two.run, args=(one, ))
    t1.daemon = True
    t1.start()
    one.run()