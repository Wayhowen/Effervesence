import queue
import time
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
    return find_element(state, 5)[0]

#Game Rules
def check_game_won(diamondsState):
    return (sorted(diamondsState) == sorted(goalState))

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
            action.append(0)
        #add the valid moves to our list
        if(check_move_valid(playerState, diamondsState, action)):
            validMoves.append(action)
    
    return validMoves

def check_move_valid(playerState, diamondsState, action):
    playerX, playerY = playerState
    #if pushing check the second space after the action
    if(action[-1] == 1):
        x, y = playerX + action[0]* 2, playerY + action[1] * 2
    else:
        x, y = playerX + action[0], playerY + action[1]
    
    blocked = diamondsState + wallsState
    return (x, y) not in blocked

def update_state(playerState, diamondsState, action):
    playerX, playerY = playerState
    newPos = playerX + action[0], playerY + action[1]
    _diamondsState = diamondsState.copy()

    #Move diamond if player moved to its space
    if (action[-1] == 1):
        _diamondsState.remove(newPos)
        _diamondsState.append((playerX + action[0] * 2, playerY + action[1] * 2))

    return newPos, sorted(_diamondsState)

def check_diamond_stuck(diamondsState):
    #List of all possible orientations from which we can view the neighbour tiles
    orientations = [[0,1,2,3,4,5,6,7,8],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6],
                    [2,5,8,1,4,7,0,3,6],
                    [6,7,8,3,4,5,0,1,2],
                    [6,3,0,7,4,1,8,5,2],
                    [8,7,6,5,4,3,2,1,0],
                    [8,5,2,7,4,1,6,3,0]
                    ]
    
    for diamond in diamondsState:
        if diamond not in goalState:
            #define neighbour tiles
            x,y = diamond
            neighbours = [(x-1,y-1),     (x-1,y),    (x-1,y+1),
                             (x,y-1),       (x,y),      (x,y+1),
                             (x+1,y-1),     (x+1,y),    (x+1,y+1)]

            #test stuck rules against each orientation
            for orientation in orientations:
                #transform neighbour view to orientation
                orientedNeighbours = [neighbours[pos] for pos in orientation]

                #check against rules
                if(orientedNeighbours[1] in wallsState and orientedNeighbours[5] in wallsState): return True
                elif(orientedNeighbours[1] in wallsState+diamondsState and orientedNeighbours[2] in wallsState+diamondsState 
                    and orientedNeighbours[5] in wallsState+diamondsState): return True
                elif(orientedNeighbours[1] in diamondsState and orientedNeighbours[2] in wallsState 
                    and orientedNeighbours[3] in wallsState and orientedNeighbours[7] in diamondsState 
                    and orientedNeighbours[8] in wallsState ): return True
    return False
    

#Search
def heuristic_distance(diamondsState):
    h_value = 0
    diamonds_and_goals = diamondsState+goalState
    exclusive_diamond_state = [i for i in diamondsState if i not in diamonds_and_goals]
    exclusive_goal_state = [i for i in goalState if i not in diamonds_and_goals]

    #Heuristic base of the distance between empty goals and their nearest open diamond
    for i in range(len(exclusive_diamond_state)):
        h_value += abs(exclusive_diamond_state[i][0]-exclusive_goal_state[i][0]) + abs(exclusive_diamond_state[i][1]-exclusive_goal_state[i][1])

    return h_value

def cost(moves):
    return len(moves)

def solve():
    player_start = find_player(state)
    diamonds_start = find_diamonds_overlap(state)
    starting_pos = (player_start, diamonds_start)

    pqueue = queue.PriorityQueue()
    explored = set()

    pqueue.put((heuristic_distance(diamonds_start),[(player_start[0],player_start[1],0)],[starting_pos]))

    #A* search
    while(pqueue):
        node = pqueue.get()
        current_state = node[-1][-1]
        current_actions = node[-2]
        player_state = node[-1][-1][0]
        diamonds_state = node[-1][-1][1]

        if(check_game_won(diamonds_state)):
            print("Path Found:")
            print(current_actions)
            #for i in range(len(current_actions)):
            #    if(i%3 == 0): print()
            #    match current_actions[i]:
            #        case (1,_,_): print("Down")
            #        case (-1,_,_): print("Up")
            #        case (_,1,_): print("Right")
            #        case (_,-1,_): print("Left")
            return

        if(str(current_state)) not in explored:
            explored.add(str(current_state))
            node_cost = cost(current_actions)

            for action in get_possible_moves(player_state,diamonds_state):
                next_player_pos, next_diamonds_pos = update_state(player_state, diamonds_state, action)
                
                if(check_diamond_stuck(diamonds_state)): continue

                total_cost = node_cost+heuristic_distance(next_diamonds_pos)
                pqueue.put((total_cost, current_actions+[(next_player_pos[0],next_player_pos[1],action[2])], node[-1]+[(next_player_pos,next_diamonds_pos)]))

    print("no path")


#Main
if __name__ == "__main__":
    start = time.time()
    input_reader = InputReader("sokoban_solver/map_input.txt")
    state = input_reader.get_map("Ozzy").enumerated()
    
    wallsState = find_walls(state)
    goalState = find_goals_overlap(state)
    solve()
    
    print("Time to calc:")
    print(time.time()-start)