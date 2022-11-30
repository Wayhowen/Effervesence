#!/usr/bin/python3
import os
from time import sleep

import dbus
import dbus.mainloop.glib


class AsebaHandler:
    def __init__(self):
        os.system("(asebamedulla ser:name=Thymio-II &) && sleep 3")
        self.aseba = self.setup()

    # ---------------------- step bullshit -----------------------
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

        # enable comm
        asebaNetwork.SendEventName("prox.comm.enable", [1])

        # scanning_thread = Process(target=robot.drive, args=(200,200,))
        return asebaNetwork

    def stopAsebamedulla(self):
        print("Stopping robot")
        os.system("pkill -n asebamedulla")
        sleep(5)
        print("asebamodulla killed")

    def dbusReply(self):
        # dbus replys can be handled here.
        # Currently ignoring
        pass

    def dbusError(self, e):
        # dbus errors can be handled here.
        # Currently only the error is logged. Maybe interrupt the mainloop here
        print("dbus error: %s" % str(e))

    ##############################################

    def drive(self, left_wheel_speed, right_wheel_speed):
        self.aseba.SendEventName("motor.target", [left_wheel_speed, right_wheel_speed])

    def stop(self):
        self.drive(0, 0)

    def get_proximity_sensor_values(self, debug=False):
        prox_horizontal = self.aseba.GetVariable("thymio-II", "prox.horizontal")
        if debug:
            print("Sensing:")
            print(prox_horizontal[0])
            print(prox_horizontal[1])
            print(prox_horizontal[2])
            print(prox_horizontal[3])
            print(prox_horizontal[4])
            print("-back-")
            print(prox_horizontal[5])
            print(prox_horizontal[6])
        return prox_horizontal

    def get_ground_sensor_values(self, debug=False):
        ground_sensor_values = self.aseba.GetVariable("thymio-II", "prox.ground.reflected")
        if debug:
            print("-ground-")
            print(ground_sensor_values)
        return ground_sensor_values

    def send_information(self, number):
        self.aseba.SendEventName("prox.comm.tx", [number])

    def receive_information(self):
        rx = self.aseba.GetVariable("thymio-II", "prox.comm.rx")
        if rx[0] != 0:
            print(rx[0])

    def light_red(self):
        self.aseba.SendEventName("leds.top", [32, 0, 0])
        self.aseba.SendEventName("leds.bottom.left", [32, 0, 0])
        self.aseba.SendEventName("leds.bottom.right", [32, 0, 0])
        self.aseba.SendEventName("leds.prox.h", [32, 32, 32, 32, 32, 32, 32, 32])
        self.aseba.SendEventName("leds.prox.v", [32, 32])
        self.aseba.SendEventName("leds.buttons", [32, 32, 32, 32])
        self.aseba.SendEventName("leds.rc", [32])
        self.aseba.SendEventName("leds.temperature", [32, 0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [0, 0, 0, 0, 0, 0, 0, 0])

    def light_blue(self):
        self.aseba.SendEventName("leds.top", [0, 0, 32])
        self.aseba.SendEventName("leds.bottom.left", [0, 0, 32])
        self.aseba.SendEventName("leds.bottom.right", [0, 0, 32])
        self.aseba.SendEventName("leds.prox.h", [0, 0, 0, 0, 0, 0, 0, 0])
        self.aseba.SendEventName("leds.prox.v", [0, 0])
        self.aseba.SendEventName("leds.buttons", [0, 0, 0, 0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0, 32])
        self.aseba.SendEventName("leds.sound", [32])
        self.aseba.SendEventName("leds.circle", [0, 0, 0, 0, 0, 0, 0, 0])

    def light_green(self):
        self.aseba.SendEventName("leds.top", [0, 32, 0])
        self.aseba.SendEventName("leds.bottom.left", [0, 32, 0])
        self.aseba.SendEventName("leds.bottom.right", [0, 32, 0])
        self.aseba.SendEventName("leds.prox.h", [0, 0, 0, 0, 0, 0, 0, 0])
        self.aseba.SendEventName("leds.prox.v", [0, 0])
        self.aseba.SendEventName("leds.buttons", [0, 0, 0, 0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0, 0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [0, 0, 0, 0, 0, 0, 0, 0])

    def light_purple(self):
        self.aseba.SendEventName("leds.top", [32, 0, 32])
        self.aseba.SendEventName("leds.bottom.left", [32, 0, 32])
        self.aseba.SendEventName("leds.bottom.right", [32, 0, 32])
        self.aseba.SendEventName("leds.prox.h", [0, 0, 0, 0, 0, 0, 0, 0])
        self.aseba.SendEventName("leds.prox.v", [0, 0])
        self.aseba.SendEventName("leds.buttons", [0, 0, 0, 0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0, 0])  # Changed
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [0, 0, 0, 0, 0, 0, 0, 0])

    def light_orange(self):
        self.aseba.SendEventName("leds.top", [32, 8, 0])
        self.aseba.SendEventName("leds.bottom.left", [32, 8, 0])
        self.aseba.SendEventName("leds.bottom.right", [32, 8, 0])
        self.aseba.SendEventName("leds.prox.h", [0, 0, 0, 0, 0, 0, 0, 0])
        self.aseba.SendEventName("leds.prox.v", [0, 0])
        self.aseba.SendEventName("leds.buttons", [0, 0, 0, 0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0, 0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [32, 32, 32, 32, 32, 32, 32, 32])
