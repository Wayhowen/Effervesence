from typing import List, Tuple
from input_reader import InputReader
from queue import PriorityQueue

#View
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
    return find_element(state, 2)

def find_goals(state: List[List[int]]):
    return find_element(state, 3)

def find_diamonds_overlap(state: List[List[int]]):
    result = find_diamonds(state)
    result.extend(find_element(state, 4))
    return result


def find_goals_overlap(state: List[List[int]]):
    result = find_goals(state)
    result.extend(find_element(state, 4))
    return result


def find_player(state: List[List[int]]):
    return find_element(state, 5)

#Rules
def check_game_won(diamondState: List[Tuple[int, int]]):
    return (sorted(diamondState) == sorted(goalState))

def get_possible_moves(playerState, diamondsState):
    #coord of direction in relation to player
    possibleAction = [[-1,0],[1,0],[0,-1],[0,1]]
    
    playerX, playerY = playerState

    validMoves = []

    for action in possibleAction:
        moveX, moveY = playerX+action[0], playerY+action[1]
        #check if player is moving (0) or pushing (1)
        if (moveX, moveY) in diamondsState:
            action.append(1)
        else:
            action.append(1)
        #add the valid moves to our list
        if(check_move_valid(playerState, diamondsState, action)):
            validMoves.append(action)
    
    return validMoves  

def check_move_valid(playerState, diamondsState, action):
    playerX, playerY = playerState
    #if pushing check the second space after the action
    if(action[-1] == 1):
        x1, y1 = playerX + 2 * action[0], playerY + 2 * action[1]
    else:
        x1, y1 = playerX + action[0], playerY + action[1]
    return (x1, y1) not in diamondsState + wallsState

#Search

#Main
if __name__ == "__main__":
    input_reader = InputReader("map_input.txt")
    state = input_reader.get_map("Claire").enumerated()
    for i in state:
        print(i)
    wallsState = find_walls(state)
    goalState = find_goals_overlap(state)
    print(check_game_won(find_diamonds(state)))
