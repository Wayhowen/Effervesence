import sys
import collections
#import numpy as np
import heapq
import os
from typing import List, Tuple

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


def find_element(state: List[List[int]], element_to_find: int) -> List[Tuple[int, int]]:
    result = []
    for row_index, row in enumerate(state):
        for column_index, element in enumerate(row):
            if element == element_to_find:
                result.append((row_index, column_index))

    return result

def find_walls(state: List[List[int]]):
    return find_element(state, 1)


def find_diamonds(state: List[List[int]]):
    return find_element(state, 2).extend(find_element(state, 4))


def find_goals(state: List[List[int]]):
    return find_element(state, 3)


def find_player(state: List[List[int]]):
    return find_element(state, 5)


if __name__ == "__main__":
    input_reader = InputReader("map_input.txt")
    state = input_reader.get_map("Claire").enumerated()
    for i in state:
        print(i)
    print(find_player(state))
    print(find_goals(state))
