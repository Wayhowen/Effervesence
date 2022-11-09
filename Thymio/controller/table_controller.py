#!/usr/bin/python3
import os

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 1")

import numpy as np
from time import sleep
import dbus
import dbus.mainloop.glib


class TableController:
    def __init__(self, actions, states, state, q_table):
        self.actions = actions
        self.states = states
        self.state = state
        self.q_table = q_table
        self.aseba = self.setup()

    def drive(self, left_wheel_speed, right_wheel_speed):
        left_wheel = left_wheel_speed
        right_wheel = right_wheel_speed
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def sens(self):
        prox_horizontal = self.aseba.GetVariable("thymio-II", "prox.horizontal")
        print("Sensing:")
        print(prox_horizontal[0])
        print(prox_horizontal[1])
        print(prox_horizontal[2])
        print(prox_horizontal[3])
        print(prox_horizontal[4])

    def detect(self):
        distance = self.aseba.GetVariable("thymio-II", "prox.horizontal")
        if distance[2] > 1500:
            print("Something infront")
            return self.states.index("INFRONT")
        elif distance[0] > 1500 or distance[1] > 1500:
            print("Something on left")
            return self.states.index("RIGHT")
        elif distance[3] > 1500 or distance[4] > 1500:
            print("Something on right")
            return self.states.index("LEFT")
        else:
            return self.states.index("EXPLORE")

    def step_function(self, action):
        if action == 0:
            self.drive(100, 100)
        elif action == 1:
            self.drive(-200, 200)
        elif action == 2:
            self.drive(200, -200)

        # time step
        sleep(0.2)

        return self.detect()

    def exec(self):
        action = np.argmax(self.q_table[self.state])

        next_state = self.step_function(action)

        self.state = next_state

    ############## Bus and aseba setup ######################################

    def setup(self):
        print("Setting up")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')

        asebaNetwork = dbus.Interface(
            asebaNetworkObject, dbus_interface='ch.epfl.mobots.AsebaNetwork'
        )
        # load the file which is run on the thymio
        asebaNetwork.LoadScripts(
            'thympi.aesl', reply_handler=self.dbusError, error_handler=self.dbusError
        )

        # scanning_thread = Process(target=robot.drive, args=(200,200,))
        return asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusReply(self):
        # dbus replys can be handled here.
        # Currently ignoring
        pass

    def dbusError(self, e):
        # dbus errors can be handled here.
        # Currently only the error is logged. Maybe interrupt the mainloop here
        print("dbus error: %s" % str(e))
