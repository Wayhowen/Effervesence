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

commands = ["straight", "left", "straight", "right", "straight",
            "left", "straight", "right", "straight", "right", "right"]


class Controls:
    def __init__(self, left_sensor, right_sensor, light_sensor):
        self.left_sensor = left_sensor
        self.right_sensor = right_sensor
        self.light_sensor = light_sensor

    def perform_command(self, current_command: str):
        if current_command == "straight":
            self.drive_straight()
        elif current_command == "left" or current_command == "right":
            self.turn(current_command)

    def drive_straight(self):
        while True:
            reflection = self.light_sensor.reflection()
            if reflection > 8:
                robot.drive(50, -5)
            elif reflection < 6:
                robot.drive(50, 5)

            lv = self.left_sensor.color()
            rv = self.right_sensor.color()
            if (lv == Color.BLACK or rv == Color.BLACK):
                ev3.speaker.beep()
                robot.straight(100)
                break

    def turn(self, command: str):
        if command == "right":
            robot.turn(-90)
            while 6 < self.light_sensor.reflection() > 8:
                robot.turn(-2)
        elif command == "left":
            robot.turn(90)
            while 6 < self.light_sensor.reflection() > 8:
                robot.turn(2)
            


if __name__ == "__main__":
    controls = Controls(left_sensor, right_sensor, light_sensor)
    for command in commands:
        controls.perform_command(command)

