from abc import abstractmethod
from typing import List, Tuple, Optional

import numpy as np
from numpy import cos, sin
from shapely.geometry import Point


class Behavior:
    def __init__(self, simulator, controller, q_table):
        self.simulator = simulator
        self.controller = controller
        self._q_table = q_table

        # mock, has to be set in each behavior
        self.states = ()
        self.actions = ()
        self._state = 0

        # used for speed measurment
        self.distances = []
        self._score = 0
        self.tagged = False
        self.last_closest_readings = [float('inf')] * len(self.controller.sensors)

        self._avoidance_action = 0
        self._avoidance_steps_left = 0

        self.forced_out_of_safezone = 0
        self._safezone_out_steps = 50
        self._safezone_forward_steps = 10
        self._allowed_to_force_others_out = True

        # uninitialized is jellow
        self._color = "#EFFF00"
        self._colors = {
            "seeking": "#FF0000",
            "safe_seeking": "#FF9100",
            "avoiding": "#2B00FF",
            "safe_avoiding": "#00FF22",
            "tagged": "#CD00FF"
        }

    @property
    def color(self):
        return self._color

    def step(self):
        self.simulator.step(self.controller)

    def perform(self, step, other_controllers):
        # move out of safezone
        action = self.check_set_behaviors(step)
        if action:
            self.perform_next_action(action)
            return
        action = np.argmax(self._q_table[self._state])
        self.perform_next_action(action)

    def check_set_behaviors(self, step: int):
        behavior_specific_action = self.behavior_specific_set_behaviors(step)
        if behavior_specific_action != None:
            return behavior_specific_action
        return self.common_set_behaviors(step)

    @abstractmethod
    def behavior_specific_set_behaviors(self, step) -> Optional[int]:
        pass

    def common_set_behaviors(self, step) -> Optional[int]:
        # line turn behavior
        left_on_line, right_on_line = self.controller.on_the_line(self.simulator.world, self.simulator.bounds)
        if right_on_line:
            return self.actions.index("GOLEFT")
        elif left_on_line:
            return self.actions.index("GORIGHT")
        # avoidance behavior -- basically turn for a bit
        if self._avoidance_steps_left:
            self._avoidance_steps_left -= 1
            return self._avoidance_action
        if self.last_closest_readings:
            if self.last_closest_readings[4] < 0.05:
                self._avoidance_steps_left = 4
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[3] < 0.05:
                self._avoidance_steps_left = 5
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[2] < 0.05:
                self._avoidance_steps_left = 6
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[1] < 0.05:
                self._avoidance_steps_left = 7
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
            elif self.last_closest_readings[0] < 0.05:
                self._avoidance_steps_left = 8
                # this has to use action that we have set on both controllers
                self._avoidance_action = self.actions.index("GOLEFT")
                return self.actions.index("GOLEFT")
        return None


    @abstractmethod
    def perform_next_action(self, action):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def callback(self, step: int, other_robots):
        pass

    @abstractmethod
    def get_score(self):
        pass

    @property
    def position(self):
        return f"{self.controller.x}, {self.controller.y}, {cos(self.controller.q) * 0.09}, {sin(self.controller.q) * 0.09}"

    @property
    def camera_range(self):
        return self.controller.get_camera_range()

    def try_tagging(self, other_robot: 'Behavior', sensor_indexes: List[int]) -> bool:
        sensors_positions = [self.controller.sensors[i].sensor_position() for i in sensor_indexes]
        if not other_robot.is_tagged and not other_robot.is_in_safezone and other_robot.can_receive(sensors_positions):
            other_robot.tagged = True
            return True
        return False

    def try_forcing_out_of_safezone(self, other_robot, sensor_indexes: List[int], step: int):
        sensors_positions = [self.controller.sensors[i].sensor_position() for i in sensor_indexes]
        if other_robot.is_in_safezone and other_robot.can_receive(sensors_positions):
            other_robot.forced_out_of_safezone = step
            return True
        return False

    @property
    def is_in_safezone(self):
        return self.controller.in_the_safezone(self.simulator.safezone)

    @property
    def is_tagged(self) -> bool:
        return self.tagged

    def robot_relative_positions_from_camera(self, robots: List['Behavior']):
        return self.controller.robots_relative_positions_from_camera(robots)

    def can_receive(self, sensors: List[Tuple[float, float, float]]):
        return any(self.controller.can_receive(Point(position[0], position[1])) for position in sensors)

