#!/usr/bin/env python2
import socket
import curses
from pan_tilt_camera_controller import pan_tilt_camera_controller

class systematic_coverage_controller(pan_tilt_camera_controller):
    def __init__(self,pan_tilt_host="192.168.0.101",pan_tilt_port=5005,curses_screen=None):
        super(keyboard_controller,self).__init__(pan_tilt_host,pan_tilt_port, curses_screen)
        # 0 is horizontal 1 is vertical
        self.orientation = 0
        self.horizontal_cell_size = 5
        self.vertical_cell_size = 5

    def boustrophedon_step(self,mode=0):
        if self.pan > self.pan_limits[1] and self.tilt > self.tilt_limits[1]:
            self.pan = self.pan_limits[0]
            self.tilt = self.tilt_limits[0]
            return
        if self.orientation = 0:
            if self.pan > self.pan_limits[1]:
                self.pan = self.pan_limits[0]:
        elif self.orientation = 1:
            if self.tilt > self.tilt_limits[1]:
                self.tilt = self.tilt_limits[0]:

    def run(self, pan_init=90.0, tilt_init=90.0):
        self.myscreen.clear()
        self.myscreen.border(0)
        self.myscreen.addstr(6, 5, "Press 'q' to go back.")
        self.myscreen.nodelay(1)
        c = ''
        self.pan=pan_init
        self.tilt=tilt_init

        while c != ord('q'):
            self.myscreen.refresh()
            c = self.myscreen.getch()
            self.myscreen.addstr(12, 25, "Pan: %f Tilt: %f"%(self.pan,self.tilt))

            self.send_pan_tilt_command(self.pan,self.tilt)

        self.disconnect()
        self.myscreen.clear()
        curses.flushinp()
        self.myscreen.nodelay(0)
        return (self.pan, self.tilt)


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
                    pan = 180.0
            elif c == curses.KEY_RIGHT:
                pan -= self.pan_speed
                if pan < 0.0:
                    pan = 0.0
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
