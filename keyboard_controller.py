#!/usr/bin/env python2
import socket
import curses
from pan_tilt_camera_controller import pan_tilt_camera_controller

class keyboard_controller(pan_tilt_camera_controller):
    def __init__(self,pan_tilt_host="192.168.0.101",pan_tilt_port=5005,curses_screen=None):
        super(keyboard_controller,self).__init__(pan_tilt_host,pan_tilt_port, curses_screen)

    def run(self):
        step = 1.0
        pan  = 90.0
        tilt = 90.0

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
                tilt += step
                if tilt > 180.0:
                    tilt = 180.0
            elif c == curses.KEY_DOWN:
                tilt -= step
                if tilt < 0.0:
                    tilt = 0.0
            elif c == curses.KEY_LEFT:
                pan += step
                if pan > 180.0:
                    pan = 180.0
            elif c == curses.KEY_RIGHT:
                pan -= step
                if pan < 0.0:
                    pan = 0.0
            elif c == curses.KEY_NPAGE:
                step -= 0.1
                if step > 10.0:
                    step = 10.0
            elif c == curses.KEY_PPAGE:
                step += 0.1
                if step < 0.1:
                    step = 0.1
            elif c == ord('r'):
                pan=90.0
                tilt=90.0
                step=1.0
            self.send_pan_tilt_command(pan,tilt)

        self.disconnect()
        self.myscreen.clear()
