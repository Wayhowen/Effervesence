#!/usr/bin/python3
from typing import List, Tuple

from controller.modules.aseba_handler import AsebaHandler


class Controller:
    def __init__(self, safezone_reading, line_reading):
        self._aseba_handler = AsebaHandler()
        self.safezone_reading = safezone_reading
        self.line_reading = line_reading

    def kill(self):
        self._aseba_handler.stop()
        self._aseba_handler.stopAsebamedulla()

    def get_proximity_sensor_values(self) -> List[int]:
        return self._aseba_handler.get_proximity_sensor_values()

    # TODO: this might not work
    def on_the_line(self) -> Tuple[bool, bool]:
        readings = self._aseba_handler.get_ground_sensor_values()
        return readings[0] < self.line_reading, readings[1] < self.line_reading

    # TODO: fix this to only happen in safezone
    def in_the_safezone(self) -> bool:
        # here we throw away right sensor info cuz its fucked up for the gray lines
        readings = self._aseba_handler.get_ground_sensor_values()
        print(readings[0], readings[1])
        return self.line_reading < readings[0] < self.safezone_reading and readings[1] > 850

    def drive(self, left_wheel_value, right_wheel_value):
        self._aseba_handler.drive(left_wheel_value, right_wheel_value)

    def start_tagging_other(self):
        self._aseba_handler.send_information(1)

    def start_forcing_others_out_of_safezone(self):
        self._aseba_handler.send_information(2)

    def start_transmitting_bs(self):
        self._aseba_handler.send_information(69)

    def receive_information(self) -> int:
        info = self._aseba_handler.receive_information()
        print(info)
        return info

    def light_red(self):
        self._aseba_handler.light_red()

    def light_blue(self):
        self._aseba_handler.light_blue()

    def light_green(self):
        self._aseba_handler.light_green()

    def light_purple(self):
        self._aseba_handler.light_purple()

    def light_orange(self):
        self._aseba_handler.light_orange()
