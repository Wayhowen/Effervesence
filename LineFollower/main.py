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
# robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=120)
robot = DriveBase(left_motor, right_motor, wheel_diameter=80, axle_track=120)

commands = [
    (1, 0, 0),
    (1, 1, 0),
    (2, 1, 0),
    (3, 1, 0),
    (3, 0, 0)
]

right_directions = ["N", "E", "S", "W"]
left_directions = ["N", "W", "S", "E"]
# commands = ["straight", "left", "straight", "right", "straight",
#             "left", "straight", "right", "straight", "right", "right"]

TURN_BY = 95


class Controls:
    def __init__(self, left_sensor, right_sensor, light_sensor):
        self.left_sensor = left_sensor
        self.right_sensor = right_sensor
        self.light_sensor = light_sensor

        self._current_position = [0, 0, 0]
        self._direction = "N"

    def _choose_direction_to_go(self, next_position) -> str:
        if next_position[0] > self._current_position[0]:
            return "N"
        elif next_position[0] < self._current_position[0]:
            return "S"
        elif next_position[1] > self._current_position[1]:
            return "E"
        elif next_position[1] < self._current_position[1]:
            return "W"

    def _prepare_commands_to_reach_position(self,
                                            next_position,
                                            direction_to_go: str
                                            ) -> list[str]:
        commands = []
        going_left = False
        if self._direction != direction_to_go:
            current_position_index = right_directions.index(self._direction)
            next_position_index = right_directions.index(direction_to_go)
            position_difference = abs(current_position_index - next_position_index)
            if position_difference > 2:
                current_position_index = left_directions.index(self._direction)
                next_position_index = left_directions.index(direction_to_go)
                position_difference = abs(current_position_index - next_position_index)
                going_left = True
                
            for _ in range(position_difference):
                if going_left or current_position_index > next_position_index:
                    commands.append("left")
                else:
                    commands.append("right")

        if next_position[2] == 1:
            commands.append("push")
        else:
            commands.append("straight")

        return commands

    def perform_command(self, current_command):
        direction_to_go = self._choose_direction_to_go(current_command)

        commands_to_perform = self._prepare_commands_to_reach_position(
            current_command, direction_to_go)

        for command in commands_to_perform:
            ev3.screen.clear()
            ev3.screen.print(self._direction)
            if command == "straight":
                self.drive_straight()
                self._current_position = current_command
            elif command == "left" or command == "right":
                self.turn(command)

    def drive_straight(self):
        while True:
            reflection = self.light_sensor.reflection()
            if reflection > 8:
                robot.drive(70, -5)
            elif reflection < 6:
                robot.drive(70, 5)

            lv = self.left_sensor.reflection()
            rv = self.right_sensor.reflection()
            if (lv < 8 or rv < 8):
                ev3.speaker.beep()
                robot.straight(165)
                break
            else:
                ev3.screen.clear()
                ev3.screen.print(lv)
                ev3.screen.print(rv)

    def turn(self, command: str):
        if command == "right":
            robot.turn(-TURN_BY)
            while 6 < self.light_sensor.reflection() > 8:
                robot.turn(-2)
            
            if right_directions.index(self._direction) + 1 != len(right_directions):
                self._direction = right_directions[right_directions.index(self._direction) + 1]
            else:
                self._direction = left_directions[left_directions.index(self._direction) - 1]
        elif command == "left":
            robot.turn(TURN_BY + 10)
            while 6 < self.light_sensor.reflection() > 8:
                robot.turn(2)
                
            if right_directions.index(self._direction) != 0:
                self._direction = right_directions[right_directions.index(self._direction) - 1]
            else:
                self._direction = left_directions[left_directions.index(self._direction) + 1]

if __name__ == "__main__":
    controls = Controls(left_sensor, right_sensor, light_sensor)
    # while True:
    #     ev3.screen.print(left_sensor.color())
    #     ev3.screen.print(left_sensor.reflection())
    #     time.sleep(0.5)
    #     ev3.screen.clear()
    for command in commands:
        controls.perform_command(command)
