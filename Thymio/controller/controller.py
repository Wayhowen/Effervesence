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

    def in_the_safezone(self) -> bool:
        readings = self._aseba_handler.get_ground_sensor_values()
        return all(self.line_reading > reading > self.safezone_reading for reading in readings)

    def drive(self, left_wheel_value, right_wheel_value):
        self._aseba_handler.drive(left_wheel_value, right_wheel_value)

    def start_tagging_other(self):
        self._aseba_handler.send_information(1)

    def start_forcing_others_out_of_safezone(self):
        self._aseba_handler.send_information(2)

    def start_transmitting_bs(self):
        self._aseba_handler.send_information(69)

    def receive_information(self) -> List[int]:
        return self._aseba_handler.receive_information()

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
