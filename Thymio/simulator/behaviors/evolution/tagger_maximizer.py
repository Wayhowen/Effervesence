import random
from typing import List, Dict, Optional

from simulator.behaviors.behavior import Behavior


class TaggerMaximizer(Behavior):
    def __init__(self, simulator, controller, q_table, total_steps):
        super().__init__(simulator, controller)
        self.states = ("AllFRONT", "INFRONT", "LEFT", "RIGHT", "LEFTFRONT", "RIGHTFRONT", "LEFTRIGHT", "NOTHING", "LINE", "BEHIND", "TOOCLOSE")
        self.actions = (
            "GOFORWARDS", "GOLEFT", "GORIGHT", "RANDOM", "LEAN_LEFT", "LEAN_RIGHT", "SLOW_FORWARDS_LEFT",
            "SLOW_FORWARDS_RIGHT", "SLOW_FORWARDS"
        )

        self._total_steps = total_steps
        self._state = self.states.index("NOTHING")
        self._fitness = 1
        self._color = self._colors["safe_seeking"]
        self._bad_behavior_penalty = 1

    def behavior_specific_set_behaviors(self, step) -> Optional[int]:
        return None

    def _choose_color(self):
        if self.is_in_safezone:
            self._color = self._colors["safe_seeking"]
            return
        self._color = self._colors["seeking"]

    def tag_other_robots(self, step, other_controllers):
        fitness_to_add = 0
        for robot in other_controllers:
            distances_to_objects = self.controller.distances_to_objects(robot.controller.body)
            distances_matched = [index for index, val in enumerate(distances_to_objects) if val < 0.09]
            if any(distances_matched):
                if self.try_tagging(robot, distances_matched):
                    fitness_to_add += self._total_steps - step
        return fitness_to_add

    def perform_next_action(self, action):
        if action == 0:
            self.controller.drive(7.41, 7.41)
        elif action == 1:
            self.controller.drive(-11.976, 11.976)
        elif action == 2:
            self.controller.drive(11.976, -11.976)
        elif action == 3:
            self.controller.drive(random.uniform(5, 11.976), random.uniform(0.01, 11.976))
        elif action == 4:
            self.controller.drive(3.7, 7.41)
        elif action == 5:
            self.controller.drive(7.41, 3.7)
        elif action == 6:
            self.controller.drive(1.85, 3.7)
        elif action == 7:
            self.controller.drive(3.7, 1.85)
        elif action == 8:
            self.controller.drive(3.7, 3.7)

    def get_next_state(self, on_line, closest_reading, other_robot_camera_positions: Dict[str, Behavior]):
        if on_line:
            return self.states.index("LINE")
        elif any(reading < 0.04 for reading in closest_reading):
            return self.states.index("TOOCLOSE")
        elif all(k in other_robot_camera_positions for k in ("l","m","r")) and all(not other_robot_camera_positions[k].istagged for k in ("l","m","r")):
            return self.states.index("ALLFRONT")
        elif all(k in other_robot_camera_positions for k in ("l","m")) and all(not other_robot_camera_positions[k].istagged for k in ("l","m")):
            return self.states.index("LEFTFRONT")
        elif all(k in other_robot_camera_positions for k in ("m", "r")) and all(not other_robot_camera_positions[k].istagged for k in ("m","r")):
            return self.states.index("RIGHTFRONT")
        elif all(k in other_robot_camera_positions for k in ("l", "r")) and all(not other_robot_camera_positions[k].istagged for k in ("l","r")):
            return self.states.index("LEFTRIGHT")
        elif other_robot_camera_positions["m"] and not other_robot_camera_positions["m"].is_tagged:
            return self.states.index("INFRONT")
        elif other_robot_camera_positions["l"] and not other_robot_camera_positions["l"].is_tagged:
            return self.states.index("LEFT")
        elif other_robot_camera_positions["r"] and not other_robot_camera_positions["r"].is_tagged:
            return self.states.index("RIGHT")
        elif closest_reading[5] < 0.09:
            return self.states.index("BEHIND")
        else:
            return self.states.index("NOTHING")

    def callback(self, step, other_robots: List[Behavior]):
        distances_to_objects = [self.controller.distances_to_objects(robot.controller.body) for robot in other_robots]
        self.last_closest_readings = min([(x, sum(x)) for x in distances_to_objects], key=lambda reading: reading[1])[0]
        other_robot_camera_positions = self.controller.robots_relative_positions_from_camera(
            other_robots
        )
        self._state = self.get_next_state(self.last_closest_readings, other_robot_camera_positions)
        score_form_tagging = self.tag_other_robots(step, other_robots)

        self.manage_rewards(score_form_tagging)

    def manage_rewards(self, score_form_tagging: int):
        self._fitness += score_form_tagging

    def save(self):
        pass

    def get_score(self):
        return self._fitness
