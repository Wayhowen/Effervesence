import sys
import collections
#import numpy as np
import heapq
import input_reader
import os

class PriorityQueue:
    def  __init__(self):
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

def LayoutReader():
    layout = input_reader.InputReader("map_input.txt").get_map("Claire")
    
    tLayout = []

    for row in layout.map:
        tLayout.append([])
        for elem in row:
            if elem == ' ': tLayout[-1].append(0)       # empty
            elif elem  == '#': tLayout[-1].append(1)    # wall
            elif elem  == '$': tLayout[-1].append(2)    # diamond
            elif elem  == '.': tLayout[-1].append(3)    # goal
            elif elem  == '*': tLayout[-1].append(4)    # diamond in goal
            elif elem  == '@': tLayout[-1].append(5)    # player
    
    return tLayout

def FindFunc(state, matchcase):
    result = []
    for rowi, row in enumerate(state):
        for coli, elem in enumerate(row):
            if elem == matchcase: result.append((rowi, coli))

    return result

def FindWalls(state):
    return FindFunc(state, 1)

def FindDiamonds(state):
    return FindFunc(state, 2).extend(FindFunc(state, 4))

def FindGoals(state):
    return FindFunc(state, 3)

def FindPlayer(state):
    return FindFunc(state, 5)

if __name__ == "__main__":
    state = LayoutReader()
    for i in state:
        print(i)
    print(FindPlayer(state))
    print(FindGoals(state))


    


    
        
