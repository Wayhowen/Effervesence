from shapely.geometry import Point

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
from q_learning import QLearner
from simulator.robot_model.controller import Controller
from simulator.simulator import Simulator


if __name__ == '__main__':
    states = ("TOO FAR", "TOO CLOSE", "PERFECT")
    actions = ("FORWARDS", "BACKWARDS", "STOP")
    q_leaner = QLearner(states, actions, states.index("PERFECT"))
    simulator = Simulator()
    controller = Controller(simulator.W, simulator.H)


    def step_function(action):
        if action == 0:
            controller.drive(0.4, 0.4)
        elif action == 1:
            controller.drive(-0.4, -0.4)
        else:
            controller.drive(0, 0)
        # step simulation
        simulator.step(controller)

        distance = controller.distances_to_wall(simulator.world)[2]
        if distance < 0.49:
            return states.index("TOO CLOSE"), -1
        elif distance > 0.51:
            return states.index("TOO FAR"), -1
        else:
            return states.index("PERFECT"), 1

    for cnt in range(5000):
        q_leaner.choose_next_action(step_function)
        # check collision with arena walls
        if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            q_leaner.save_q_table()

    q_leaner.save_q_table()

    print(q_leaner.q_table)
            #
            # # check collision with arena walls
            # if simulator.world.distance(Point(controller.x, controller.y)) < simulator.L / 2:
            #     break
