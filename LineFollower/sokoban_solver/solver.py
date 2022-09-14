import sys
import collections
#import numpy as np
import heapq
import os

from input_reader import InputReader


class PriorityQueue:
    def __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0


def find_function(state, matchcase):
    result = []
    for rowi, row in enumerate(state):
        for coli, elem in enumerate(row):
            if elem == matchcase:
                result.append((rowi, coli))

    return result

def find_walls(state):
    return find_function(state, 1)


def find_diamonds(state):
    return find_function(state, 2).extend(find_function(state, 4))


def find_goals(state):
    return find_function(state, 3)


def find_player(state):
    return find_function(state, 5)


if __name__ == "__main__":
    input_reader = InputReader("map_input.txt")
    state = input_reader.get_map("Claire").enumerated()
    for i in state:
        print(i)
    print(find_player(state))
    print(find_goals(state))
