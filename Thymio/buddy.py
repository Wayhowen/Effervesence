import time

MAP_SIZE_PIXELS = 250
MAP_SIZE_METERS = 15
LIDAR_DEVICE = '/dev/ttyUSB0'


class BuddySaver:
    def __init__(self, lidar):
        self.lidar = lidar

    def main_loop(self, delay):
        while True:
            pos = self.lidar.getPosition()
            print(f"x:{pos[0]} y:{pos[1]} theta {pos[2]}")
            time.sleep(delay)

    def stop(self):
        self.lidar.stop()