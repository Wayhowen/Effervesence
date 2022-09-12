#!/usr/bin/env pybricks-micropython

"""
Example LEGO® MINDSTORMS® EV3 Robot Educator Driving Base Program
-----------------------------------------------------------------

This program requires LEGO® EV3 MicroPython v2.0.
Download: https://education.lego.com/en-us/support/mindstorms-ev3/python-for-ev3

Building instructions can be found at:
https://education.lego.com/en-us/support/mindstorms-ev3/building-instructions#robot
"""

import time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase
from pybricks.nxtdevices import LightSensor

# Initialize the EV3 Brick.
ev3 = EV3Brick()

# Initialize the motors.
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)

# Initialize the color sensors
left_sensor = ColorSensor(Port.S1)
right_sensor = ColorSensor(Port.S4)

# Initialize infrared sensors
light_sensor = LightSensor(Port.S2)

# Initialize the drive base.
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=120)


def turning_coroutine(direction: str, left_sensor_reading: Color, right_sensor_reading: Color):
    if direction == "left":
        if left_sensor_reading == Color.BLACK:
            robot.drive(50, 45)
        elif right_sensor_reading == Color.BLACK:
            robot.drive(50, -45)
    elif direction == "right":
        if right_sensor_reading == Color.BLACK:
            robot.drive(50, -45)
        elif left_sensor_reading == Color.BLACK:
            robot.drive(50, 45)


turns_done = 0
last_angle = robot.angle()

while True:
    lv = left_sensor.color()
    rv = right_sensor.color()

    if turns_done % 2 == 0:
        turning_coroutine("left", lv, rv)
    elif turns_done % 2 == 1:
        turning_coroutine("right", lv, rv)

    if abs(robot.angle() - last_angle) > 85:
        turns_done += 1
        ev3.speaker.beep()
        last_angle = robot.angle()

    ev3.screen.clear()
    ev3.screen.print(light_sensor.reflection())
    ev3.screen.print(light_sensor.ambient())

    robot.drive(100, 0)
