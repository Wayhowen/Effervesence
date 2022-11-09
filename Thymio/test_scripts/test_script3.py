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
        self.proxSensorsVal=[0,0,0,0,0]
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

    def get_variables_reply(self, r):
        global proxSensorsVal
        proxSensorsVal=r
    
    def get_variables_error(self, e):
        print('error:')
        print(str(e))
 
    def Braitenberg(self):
        #get the values of the sensors
        self.aseba.GetVariable("thymio-II", "prox.horizontal",reply_handler=self.get_variables_reply,error_handler=self.get_variables_error)
    
        #print the proximity sensors value in the terminal
        print(self.proxSensorsVal[0],self.proxSensorsVal[1],self.proxSensorsVal[2],self.proxSensorsVal[3],self.proxSensorsVal[4])
    
        #Parameters of the Braitenberg, to give weight to each wheels
        leftWheel=[-0.01,-0.005,-0.0001,0.006,0.015]
        rightWheel=[0.012,+0.007,-0.0002,-0.0055,-0.011]
    
        #Braitenberg algorithm
        totalLeft=0
        totalRight=0
        for i in range(5):
            totalLeft=totalLeft+(self.proxSensorsVal[i]*leftWheel[i])
            totalRight=totalRight+(self.proxSensorsVal[i]*rightWheel[i])
    
        #add a constant speed to each wheels so the robot moves always forward
        totalRight=totalRight+50
        totalLeft=totalLeft+50
    
        #print in terminal the values that is sent to each motor
        print("totalLeft")
        print(totalLeft)
        print("totalRight")
        print(totalRight)
    
        #send motor value to the robot
        self.aseba.SetVariable("thymio-II", "motor.left.target", [totalLeft])
        self.aseba.SetVariable("thymio-II", "motor.right.target", [totalRight])    
    
        return True

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
 
if __name__ == '__main__':
    robot = Thymio()
    try:
        while True:
            robot.Braitenberg()
    finally:
        print("Stopping robot")
        exit_now = True
        sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")