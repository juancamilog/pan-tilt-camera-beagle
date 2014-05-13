#!/usr/bin/env python2
import socket
import curses

class pan_tilt_camera_controller(object):
    def __init__(self,pan_tilt_host="192.168.0.101",pan_tilt_port=5005,curses_screen=None):
        self.udp_sock = None

        self.udp_host = pan_tilt_host
        self.udp_port = int(pan_tilt_port)

        self.pan = 90.0
        self.tilt = 90.0

        if curses_screen is None:
            self.myscreen = curses.initscr()
            self.myscreen.keypad(1)
            curses.noecho()
            curses.cbreak()
            self.myscreen.border(0)
        else:
            self.myscreen = curses_screen

    def connect(self):
        if self.udp_sock is not None:
            self.disconnect()
        self.udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp_sock.connect((self.udp_host,self.udp_port))

    def disconnect(self):
        self.udp_sock.close()
        self.udp_sock = None

    def send_pan_tilt_command(self,pan,tilt):
        self.pan = pan
        self.tilt = tilt

        msg = str(pan)+','+str(tilt)
        self.udp_sock.sendto(msg, (self.udp_host, self.udp_port))

    def run(self, pan_init, tilt_init):
        pass
