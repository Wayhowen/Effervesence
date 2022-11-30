#!/usr/bin/python3
import traceback

from controller.behaviors.tagger import Tagger


if __name__ == '__main__':
    try:
        # TODO: choose the values
        behavior = Tagger(line_reading=300, safezone_reading=850, five_cm_reading=2500, nine_cm_reading=1200, max_speed=500)
        behavior.run(steps=1800)

    except Exception as e:
        traceback.print_exc()
        behavior.kill()
