from numpy import cos, sin

from simulator.robot_model.sensor.sensor import Sensor


class BackSensor(Sensor):
    def __init__(self, W, H, offset: float, position_getter, backward_offset_cm, side_offset_cm, side_offset_radians):
        super().__init__(W, H, offset, position_getter)
        self._backward_offset_cm = backward_offset_cm
        self._side_offset_cm = side_offset_cm
        self._side_offset_radians = side_offset_radians

    def _sensor_position(self):
        x, y, q = self._position_getter()
        offset_q = q + self.offset

        # move backwards
        x = x + cos(offset_q) * self._backward_offset_cm
        y = y + sin(offset_q) * self._backward_offset_cm

        # move to the sides
        x = x + cos(offset_q + self._side_offset_radians) * self._side_offset_cm
        y = y + sin(offset_q + self._side_offset_radians) * self._side_offset_cm

        return x, y, offset_q