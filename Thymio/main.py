import threading

from buddy import BuddySaver
from controller.lidar import Lidar

if __name__ == "__main__":

    # initialize modules and pass them to controller buddySaver
    lidar = Lidar()
    saver = BuddySaver(lidar)

    # TODO: Move this to lidar and implement correct start and stop methods
    # this might not work tho.. so we need to test it
    t1 = threading.Thread(target=lidar.updateLidar, args=('thread1', 0.1))
    t1.daemon = True
    t1.start()
    try:
        while True:
            saver.main_loop(0.1)

    except KeyboardInterrupt:
        t1.join()
        saver.stop()
        exit(0)
