from numpy import cos, sin

from simulator.robot_model.sensor.sensor import Sensor


class SideSensor(Sensor):
    def __init__(self, W, H, offset: float, position_getter, sensor_forward_offset=0.08):
        super().__init__(W, H, offset, position_getter)
        self._sensor_forward_offset = sensor_forward_offset

    def _sensor_position(self):
        x, y, q = self._position_getter()
        offset_q = q + self.offset
        x = x + cos(offset_q) * self._sensor_forward_offset
        y = y + sin(offset_q) * self._sensor_forward_offset
        return x, y, offset_q