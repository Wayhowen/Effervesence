from numpy import sin, cos

from simulator.robot_model.controller import Controller
from shapely.geometry import LinearRing


class Simulator:
    def __init__(self):
        self.R = 0.0225  # radius of wheels in meters
        self.L = 0.095  # distance between wheels in meters

        self.W = 2.0  # width of arena
        self.H = 2.0  # height of arena

        # the world is a rectangular arena with width W and height H
        self.world = LinearRing(
            [
                (self.W / 2, self.H / 2),
                (-self.W / 2, self.H / 2),
                (-self.W / 2, -self.H / 2),
                (self.W / 2, -self.H / 2)
            ])

        self.robot_timestep = 0.1  # 1/robot_timestep equals update frequency of robot
        self.simulation_timestep = 0.01  # timestep in kinematics sim (probably don't touch..)

    # Kinematic model
    #################
    # updates robot position and heading based on velocity of wheels and the elapsed time
    # the equations are a forward kinematic model of a two-wheeled robot - don't worry just use it
    def step(self, controller: Controller):
        for step in range(int(self.robot_timestep / self.simulation_timestep)):  # step model time/timestep times
            v_x = cos(controller.q) * (
                        self.R * controller.left_wheel_velocity / 2 + self.R * controller.right_wheel_velocity / 2)
            v_y = sin(controller.q) * (
                        self.R * controller.left_wheel_velocity / 2 + self.R * controller.right_wheel_velocity / 2)
            omega = (self.R * controller.right_wheel_velocity - self.R * controller.left_wheel_velocity) / (2 * self.L)

            controller.x += v_x * self.simulation_timestep
            controller.y += v_y * self.simulation_timestep
            controller.q += omega * self.simulation_timestep
