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
from pybricks.ev3devices import Motor, ColorSensor, InfraredSensor
from pybricks.parameters import Port, Color
from pybricks.robotics import DriveBase

# Initialize the EV3 Brick.
ev3 = EV3Brick()

# Initialize the motors.
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)

# Initialize the color sensors
left_sensor = ColorSensor(Port.S1)
right_sensor = ColorSensor(Port.S4)

# Initialize infrared sensors
# ir_sensor = ColorSensor(Port.S2)

# Initialize the drive base.
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=120)


# def detectionCouroutine(robot: DriveBase, color_sensor: ColorSensor):
#     if color_sensor.color() == Color.BLACK:
#         robot.


while True:
    # turned = False
    lv = left_sensor.color()
    rv = right_sensor.color()

    # if lv == Color.BLACK and rv == Color.BLACK:
    #    robot.drive(-75, 0)
    #     robot.turn(90)
    #     robot.straight(-150)
    if lv == Color.BLACK:
        robot.drive(50, 45)
    elif rv == Color.BLACK:
        robot.drive(50, -45)
    else:
        robot.drive(100, 0)
