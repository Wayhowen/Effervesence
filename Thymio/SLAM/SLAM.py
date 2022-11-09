from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar

MAP_SIZE_PIXELS         = 250
MAP_SIZE_METERS         = 15
LIDAR_DEVICE            = '/dev/ttyUSB0'

# Pose will be modified in our threaded code
pose = [0, 0, 0]


# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 100



# from roboviz import MapVisualizer

if __name__ == '__main__':

    # Connect to Lidar unit
    lidar = Lidar(LIDAR_DEVICE)

    # Create an RMHC SLAM object with a laser model and optional robot model
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    # Set up a SLAM display
    #viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')

    # Initialize an empty trajectory
    trajectory = []

    # Initialize empty map
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

    # Create an iterator to collect scan data from the RPLidar
    iterator = lidar.iter_scans()

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    # First scan is crap, so ignore it
    next(iterator)
    pose = [0, 0, 0]
    gpose = [0, 0, 0]

    while True:

        # Extract (quality, angle, distance) triples from current scan
        # print(next(iterator))
        items = [item for item in next(iterator)]

        # Extract distances and angles from triples
        distances = [item[2] for item in items]
        angles    = [item[1] for item in items]

        # Update SLAM with current Lidar scan and scan angles if adequate
        if len(distances) > MIN_SAMPLES:
            slam.update(distances, scan_angles_degrees=angles)
            previous_distances = distances.copy()
            previous_angles    = angles.copy()

        # If not adequate, use previous
        elif previous_distances is not None:
            slam.update(previous_distances, scan_angles_degrees=previous_angles)

        # Get current robot position
        pose[0], pose[1], pose[2] = slam.getpos()

        gpose[0], gpose[1], gpose[2] = pose[0]/60, pose[1]/60, pose[2]

        # Get current map bytes as grayscale
        slam.getmap(mapbytes)
        print(f"x:{pose[0]} y:{pose[1]} theta {pose[2]}")

        print(f"gx:{gpose[0]} gy:{gpose[1]} theta {gpose[2]}")

        # Display map and robot pose, exiting gracefully if user closes it
        # if not viz.display(x/1000., y/1000., theta, mapbytes):
        #    exit(0)
        # Shut down the lidar connection
    lidar.stop()
    lidar.disconnect()

def getPosition():
    return pose

def getMap():
    return mapbytes

def getGridPosition():
    gridX = int(pose[0]/60)
    gridY = int(pose[1]/60) 
    return [gridX, gridY, pose[2]]
