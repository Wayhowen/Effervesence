#!/usr/bin/python3
# this shit library has to be installed weirdly
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar
import time

MAP_SIZE_PIXELS = 250
MAP_SIZE_METERS = 15
LIDAR_DEVICE = '/dev/ttyUSB0'
# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES = 50


class Lidar:
    def __init__(self):
        # Pose will be modified in our threaded code
        self.pose = [0, 0, 0]

        # Connect to Lidar unit
        self.lidar = RPLidar(LIDAR_DEVICE)
        # Initialize an empty trajectory
        self.trajectory = []

        # Initialize empty map
        self.map_bytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
        # Create an RMHC SLAM object with a laser model and optional robot model
        self.slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

        self._run_thread = True

    def stop(self):
        self._run_thread = False
        self.lidar.stop()
        self.lidar.disconnect()

    def updateLidar(self, thread_name, delay):
        # Set up a SLAM display
        # viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
        # Create an iterator to collect scan data from the RPLidar
        iterator = self.lidar.iter_scans()

        # We will use these to store previous scan in case current scan is inadequate
        previous_distances = None
        previous_angles = None

        # First scan is crap, so ignore it
        next(iterator)

        while self._run_thread:
            # Extract (quality, angle, distance) triples from current scan
            # print(next(iterator))
            items = [item for item in next(iterator)]

            # Extract distances and angles from triples
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                self.slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles = angles.copy()

            # If not adequate, use previous
            elif previous_distances is not None:
                self.slam.update(previous_distances, scan_angles_degrees=previous_angles)

            # Get current robot position
            self.pose[0], self.pose[1], self.pose[2] = self.slam.getpos()

            # Get current map bytes as grayscale
            self.slam.getmap(self.map_bytes)
            time.sleep(delay)

    def get_position(self):
        return self.pose

    def get_map(self):
        return self.map_bytes
