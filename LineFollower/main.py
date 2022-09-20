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

# Claire
#command = [(1, 2, 0), (2, 2, 1), (3, 2, 1), (3, 3, 0), (4, 3, 0), (4, 4, 0), (4, 5, 0), (3, 5, 0), (3, 4, 1), (3, 5, 0), (2, 5, 0), (2, 4, 1), (2, 3, 1), (3, 3, 1), (3, 2, 0), (3, 1, 0), (2, 1, 1)]

commands = [
    (1, 0, 0),
    (1, 1, 0),
    (2, 1, 0),
    (3, 1, 0),
    (3, 0, 0)
]

right_directions = ["N", "E", "S", "W"]
left_directions = ["N", "W", "S", "E"]

TURN_BY = 95
DRIVE_SPEED = 70
DRIVE_ADJUSTMENT_ANGLE = 5
LOWER_REFLECTION_BOUNDARY = 6
UPPER_REFLECTION_BOUNDARY = 8

"""
possible commands are:
straight
push
left
right
turnaround
backwards -- needs implementation
"""
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

    """
    This is basically a plan translator
    """
    def _prepare_commands_to_reach_position(self,
                                            next_position,
                                            direction_to_go: str
                                            ) -> list[str]:
        commands = []
        going_left = False
        if self._direction != direction_to_go:
            # find how many turns we have to do
            current_position_index = right_directions.index(self._direction)
            next_position_index = right_directions.index(direction_to_go)
            position_difference = abs(current_position_index - next_position_index)
            # if more than 2, then there is a better alternative available surely
            if position_difference > 2:
                current_position_index = left_directions.index(self._direction)
                next_position_index = left_directions.index(direction_to_go)
                position_difference = abs(current_position_index - next_position_index)
                going_left = True
                
            if position_difference == 1:
                if going_left or current_position_index > next_position_index:
                    commands.append("left")
                else:
                    commands.append("right")
            elif position_difference == 2:
                commands.append("turnaround")

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
            elif command == "push":
                self.drive_straight(True)
                self._current_position = current_command
            elif command == "left" or command == "right" or command == "turnaround":
                self.turn(command)

    def drive_straight(self, pushing = False):
        while True:
            reflection = self.light_sensor.reflection()
            if reflection > UPPER_REFLECTION_BOUNDARY:
                robot.drive(DRIVE_SPEED, -DRIVE_ADJUSTMENT_ANGLE)
            elif reflection < LOWER_REFLECTION_BOUNDARY:
                robot.drive(DRIVE_SPEED, DRIVE_ADJUSTMENT_ANGLE)

            lv = self.left_sensor.reflection()
            rv = self.right_sensor.reflection()
            if (lv < UPPER_REFLECTION_BOUNDARY or rv < UPPER_REFLECTION_BOUNDARY):
                ev3.speaker.beep()
                if not pushing:
                    robot.straight(165)
                    break
                self.drive_backwards()
            # just a debugging statement
            else:
                ev3.screen.clear()
                ev3.screen.print(lv)
                ev3.screen.print(rv)
    
    # TODO: inverse of forwards, not tested
    def drive_backwards(self):
        while True:
            reflection = self.light_sensor.reflection()
            if reflection > UPPER_REFLECTION_BOUNDARY:
                robot.drive(DRIVE_SPEED, DRIVE_ADJUSTMENT_ANGLE)
            elif reflection < LOWER_REFLECTION_BOUNDARY:
                robot.drive(DRIVE_SPEED, -DRIVE_ADJUSTMENT_ANGLE)

            lv = self.left_sensor.reflection()
            rv = self.right_sensor.reflection()
            if (lv < UPPER_REFLECTION_BOUNDARY or rv < UPPER_REFLECTION_BOUNDARY):
                ev3.speaker.beep()
                robot.straight(165)
                break

    """
    This if statements allow for easier choosing of the current directions after turn
    """
    def turn(self, command: str):
        if command == "right":
            robot.turn(-TURN_BY)
            while LOWER_REFLECTION_BOUNDARY < self.light_sensor.reflection() > UPPER_REFLECTION_BOUNDARY:
                robot.turn(-2)
            
            if right_directions.index(self._direction) + 1 != len(right_directions):
                self._direction = right_directions[right_directions.index(self._direction) + 1]
            else:
                self._direction = left_directions[left_directions.index(self._direction) - 1]
        elif command == "left":
            # TODO: this is where the code fails with plows
            robot.turn(TURN_BY)
            while LOWER_REFLECTION_BOUNDARY < self.light_sensor.reflection() > UPPER_REFLECTION_BOUNDARY:
                robot.turn(2)
                
            if right_directions.index(self._direction) != 0:
                self._direction = right_directions[right_directions.index(self._direction) - 1]
            else:
                self._direction = left_directions[left_directions.index(self._direction) + 1]
                
        elif command == "turnaround":
            robot.turn(2 * TURN_BY)
            while LOWER_REFLECTION_BOUNDARY < self.light_sensor.reflection() > UPPER_REFLECTION_BOUNDARY:
                robot.turn(2)
            if self._direction == "N":
                self._direction = "S"
            elif self._direction == "E":
                self._direction = "W"
            elif self._direction == "S":
                self._direction = "N"
            elif self._direction == "W":
                self._direction = "E"

if __name__ == "__main__":
    controls = Controls(left_sensor, right_sensor, light_sensor)
    # while True:
    #     ev3.screen.print(left_sensor.color())
    #     ev3.screen.print(left_sensor.reflection())
    #     time.sleep(0.5)
    #     ev3.screen.clear()
    for command in commands:
        controls.perform_command(command)
