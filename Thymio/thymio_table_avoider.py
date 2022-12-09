#!/usr/bin/python3
import threading
import time
import traceback

from controller.behaviors.tagger import Tagger
from controller.behaviors.avoider import Avoider


def tagged_checker(avoider: Avoider):
    tagged = False
    while not tagged:
        tagged = avoider.is_tagged() and not avoider.controller.in_the_safezone()
        if avoider.is_forced_out_of_safezone() and avoider.forced_out_of_safezone == 0:
            avoider.set_forced_out_of_safezone()
        time.sleep(0.1)
    lock = threading.Lock()
    with lock:
        avoider.set_alive(False)


if __name__ == '__main__':
    try:
        # TODO: choose the values
        # Other guys robot
        #behavior = Tagger(left_line_reading=200, right_line_reading=250, safezone_reading=400, five_cm_reading=2500, nine_cm_reading=1200, max_speed=500)
        # good base settings - Tagger
        # behavior = Tagger(left_line_reading=250, right_line_reading=250, safezone_reading=800, five_cm_reading=2500, nine_cm_reading=1200, max_speed=400)
        behavior = Avoider(left_line_reading=250, right_line_reading=250, safezone_reading=800, five_cm_reading=500, nine_cm_reading=200, max_speed=400)
        
        if isinstance(behavior, Avoider):
            t1 = threading.Thread(target=tagged_checker, args=(behavior,))
            t1.daemon = True
            t1.start()

        behavior.run(steps=1800)

    except Exception as e:
        traceback.print_exc()
    finally:
        behavior.kill()
        print("Stopping robot")
