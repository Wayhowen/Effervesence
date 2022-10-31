#!/usr/bin/python3
import os

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
import matplotlib.pyplot as plt
from time import sleep
import dbus
import dbus.mainloop.glib
from threading import Thread

class Thymio:
    def __init__(self):
        self.aseba = self.setup()

    def move(self):
        count = 1
        left_wheel_velocity = -200
        right_wheel_velocity = 200
        # Get initial sensor values

        while count < 500:
            self.drive(left_wheel_velocity,right_wheel_velocity)
            #robot.sens()
            count += 1

        self.stop()
    
    def turn(self, l, r):
        left_wheel_velocity = l
        right_wheel_velocity = r
        # Get initial sensor values
        self.drive(left_wheel_velocity,right_wheel_velocity)

    def drive(self, left_wheel_speed, right_wheel_speed):
        #print("Left_wheel_speed: " + str(left_wheel_speed))
        #print("Right_wheel_speed: " + str(right_wheel_speed))

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
        prox_horizontal = self.aseba.GetVariable("thymio-II", "prox.horizontal")
        if prox_horizontal[2] > 2000:
            return "INFRONT"
        elif prox_horizontal[0] > 2000 or prox_horizontal[1] > 2000:
            return "LEFT"
        elif prox_horizontal[3] > 2000 or prox_horizontal[4] > 2000:
            return "RIGHT"
        else:
            return "EXPLORE"
    
    def act(self, action):
        if action == "GOFORWARDS":
            self.drive(50,50)
            sleep(0.2)
            self.stop()
        elif action == "GOBACKWARDS":
            self.drive(-50,-50)
            sleep(0.2)
            self.stop()
        elif action == "GOLEFT":
            self.drive(-100,100)
            sleep(0.2)
            self.stop()
        elif action == "GORIGHT":
            self.drive(100,-100)
            sleep(0.2)
            self.stop()
        else:
            self.stop()

    def explore(self, action):
        self.act(action)
        state = self.detect()

        return state


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


# ------------------ Main -------------------------

def main():
    while True:
        dist = robot.detect()
        if dist == "INFRONT":
            robot.act("GOBACKWARDS")
        elif dist == "LEFT":
            robot.act("GORIGHT")
        elif dist == "RIGHT":
            robot.act("GOLEFT")
        else:
            robot.act("GOFORWARDS")


# ------------------- Main ------------------------

if __name__ == '__main__':
    try:
        robot = Thymio()
        main()
    except:
        print("Stopping robot")
        robot.stop()
        exit_now = True
        sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
