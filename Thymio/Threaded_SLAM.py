from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
import threading
import time
import PIL.Image as Image
from ThymioController import Thymio 

MAP_SIZE_PIXELS         = 250
MAP_SIZE_METERS         = 15
LIDAR_DEVICE            = '/dev/ttyUSB0'

# Pose will be modified in our threaded code
pose = [0, 0, 0]


# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 100
# Connect to Lidar unit
lidar = Lidar(LIDAR_DEVICE)
# Initialize an empty trajectory
trajectory = []

# Initialize empty map
mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
# Create an RMHC SLAM object with a laser model and optional robot model
slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
pose = [0, 0, 0]
runThread = True

def updateLidar(thread_name, delay):
    # Set up a SLAM display
    # viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    # Create an iterator to collect scan data from the RPLidar
    iterator = lidar.iter_scans()

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    # First scan is crap, so ignore it
    next(iterator)

    while runThread:

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
        print(f"x:{pose[0]/60} y:{pose[1]/60} theta {pose[2]}")
        # Get current map bytes as grayscale
        slam.getmap(mapbytes)
        time.sleep(delay)

def getPosition():
    return pose

def getMap():
    return mapbytes

def getGridPosition():
    gridX = int(pose[0]/60)
    gridY = int(pose[1]/60) 
    return [gridX, gridY, pose[2]]

def saveMap():
    image = Image.frombuffer('L', (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), mapbytes, 'raw', 'L', 0, 1)
    image.save("map.jpg")

def move(steps):
    speed = 190
    robot.drive(speed, speed)
    time.sleep(steps)
    robot.stop()

def turn(angle, delay):
    pos = getGridPosition()
    count = 0
    speed = 32
    theta = pos[2]+angle
    cycle_time = time.time()
    #time.sleep(5)

    while True:
        pos = getGridPosition()
        print(pos[2])
        if pos[2] < theta+1 and pos[2] > theta-1:
            robot.stop()
            time.sleep(5)
            break
        if count % 2 == 0:
            if pos[2] > theta+1:
                robot.turn(-speed, speed)
            elif pos[2] < theta-1:
                robot.turn(speed, -speed)
                
        
        count = count+1

        # makes turning more precise overtimer
        if time.time()-cycle_time > 20.0 and speed>8:
            print("slow down")
            speed = speed/2
            cycle_time = time.time()
        
        #for "threading"
        time.sleep(delay)

if __name__ == "__main__":
    t1 = threading.Thread(target=updateLidar, args=('thread1', 0.0))
    t1.daemon = True
    t1.start()
    robot = Thymio()

    try:
        while True:
            val = input("Next command:")
            print(val)
            if val == "w":
                move(1)
            elif val == "a":
                turn(-90,0.1)
            elif val == "d":
                turn(90,0.1)
            elif val == "q":
                break
        saveMap()
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        runThread = False
        #t1.join()
        lidar.stop()
        lidar.disconnect()
        robot.stop()
        robot.stopAsebamedulla()
        print("asebamodulla killed")
        exit(0)