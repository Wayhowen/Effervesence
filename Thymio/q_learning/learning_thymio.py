#!/usr/bin/python3
import os

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")

from q_learning import QLearner
from time import sleep
import dbus
import dbus.mainloop.glib


class Thymio:
    def __init__(self, actions, states):
        self.actions = actions
        self.states = states
        self.aseba = self.setup()

    def drive(self, left_wheel_speed, right_wheel_speed):
        # print("Left_wheel_speed: " + str(left_wheel_speed))
        # print("Right_wheel_speed: " + str(right_wheel_speed))

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

    def detect(self, reward):
        distance = self.aseba.GetVariable("thymio-II", "prox.horizontal")
        if distance[2] < 3000:
            return self.states.index("INFRONT"), -10-reward
        elif distance[0] < 3000 or distance[1] < 3000:
            return self.states.index("LEFT"), reward+10
        elif distance[3] < 3000 or distance[4] < 3000:
            return self.states.index("RIGHT"), reward+10
        else:
            return self.states.index("EXPLORE"), reward+10

    def step_function(self, action):
        reward = 0
        if action == 0:
            self.drive(100, 100)
            reward += 10
        elif action == 1:
            self.drive(-200, 200)
        elif action == 2:
            self.drive(200, -200)

        # time step
        sleep(0.2)

        return self.detect(reward)

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

def main(controller, q):
    for cnt in range(10000):
        q.choose_next_action(controller.perform_next_action)


# ------------------- Main ------------------------

if __name__ == '__main__':
    try:
        states = ("INFRONT", "LEFT", "RIGHT", "EXPLORE")
        actions = ("GOFORWARDS", "GOLEFT", "GORIGHT")
        controller = Thymio(actions, states)
        q_leaner = QLearner(states, actions, states.index("EXPLORE"))
        main(controller, q_leaner)
    except:
        print("Stopping robot")
        controller.stop()
        sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
    finally:
        print(q_leaner.q_table)
        q_leaner.save_q_table()
