#!/usr/bin/env python2
import socket
import curses
from pan_tilt_camera_controller import pan_tilt_camera_controller

class keyboard_controller(pan_tilt_camera_controller):
    def __init__(self,pan_tilt_host="192.168.0.101",pan_tilt_port=5005,curses_screen=None):
        super(keyboard_controller,self).__init__(pan_tilt_host,pan_tilt_port, curses_screen)

    def run(self, pan_init=90.0,tilt_init=90.0):
        step = 1.0
        pan  = pan_init
        tilt = tilt_init

        self.myscreen.clear()

        self.myscreen.border(0)
        self.myscreen.addstr(3, 5, "Control tilt with UP/DOWN.")
        self.myscreen.addstr(4, 5, "Control pan with LEFT/RIGHT.")
        self.myscreen.addstr(5, 5, "Change step size with PG UP/PG DOWN.")
        self.myscreen.addstr(6, 5, "Press 'q' to go back.")
        c = ''

        while c != ord('q'):
            self.myscreen.addstr(12, 25, "Pan: %f Tilt: %f"%(self.pan,self.tilt))
            self.myscreen.addstr(13, 25, "Step size: %f"%(step))
            self.myscreen.refresh()
            c = self.myscreen.getch()
            if c == curses.KEY_HOME:
                pan = tilt = 90.0
            elif c == curses.KEY_UP:
                tilt += self.tilt_speed
                if tilt > 180.0:
                    tilt = 180.0
            elif c == curses.KEY_DOWN:
                tilt -= self.tilt_speed
                if tilt < 0.0:
                    tilt = 0.0
            elif c == curses.KEY_LEFT:
                pan += self.pan_speed
                if pan > 180.0:
                    pan = 0.0
                    tilt = 180 - tilt
            elif c == curses.KEY_RIGHT:
                pan -= self.pan_speed
                if pan < 0.0:
                    pan = 180.0
                    tilt = 180 - tilt
            elif c == curses.KEY_NPAGE:
                self.pan_speed -= 0.1
                self.tilt_speed -= 0.1
                if self.pan_speed > 10.0:
                    self.pan_speed = 10.0
                    self.tilt_speed = 10.0
            elif c == curses.KEY_PPAGE:
                self.pan_speed += 0.1
                self.tilt_speed += 0.1
                if self.pan_speed < 0.1:
                    self.pan_speed = 0.1
                    self.tilt_speed = 0.1
            elif c == ord('r'):
                pan=90.0
                tilt=90.0
                self.pan_speed=1.0
                self.tilt_speed=1.0
            self.send_pan_tilt_command(pan,tilt)

        self.disconnect()
        self.myscreen.clear()
        return (pan,tilt)
