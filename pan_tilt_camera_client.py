#!/usr/bin/env python

import socket
import curses
import signal

UDP_HOST = "192.168.0.101"
UDP_PORT = 5005
udp_sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


def exit_gracefully(signum, frame):
    global myscreen
    signal.signal(signal.SIGTERM, original_sigint)
    signal.signal(signal.SIGABRT, original_sigint)
    signal.signal(signal.SIGINT, original_sigint)
    
    exit()

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)    

def exit():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def send_udp_command(pan,tilt):
    global udp_sock
    global UDP_HOST
    global UDP_PORT
    msg = str(pan)+','+str(tilt)
    udp_sock.sendto(msg, (UDP_HOST, UDP_PORT))

def keyboard_controller(myscreen):
    step = 1.0
    pan  = 90
    tilt = 90
    myscreen.addstr(3, 5, "Control tilt with UP/DOWN.")
    myscreen.addstr(4, 5, "Control pan with LEFT/RIGHT.")
    myscreen.addstr(5, 5, "Change step size with PG UP/PG DOWN.")
    myscreen.addstr(6, 5, "Press 'q' to exit.")
    c = ''
    while c != ord('q'):
        myscreen.addstr(12, 25, "Pan: %f Tilt: %f"%(pan,tilt))
        myscreen.addstr(13, 25, "Step size: %f"%(step))
        myscreen.refresh()
        c = myscreen.getch()
        if c == curses.KEY_HOME:
            pan = tilt = 90.0
        elif c == curses.KEY_UP:
            tilt += step
            if tilt > 180:
                tilt = 180
        elif c == curses.KEY_DOWN:
            tilt -= step
            if tilt < 0:
                tilt = 0
        elif c == curses.KEY_LEFT:
            pan += step
            if pan > 180:
                pan = 180
        elif c == curses.KEY_RIGHT:
            pan -= step
            if pan < 0:
                pan = 0
        elif c == curses.KEY_NPAGE:
            step -= 0.1
            if step > 10:
                step = 10
        elif c == curses.KEY_PPAGE:
            step += 0.1
            if step < 0.1:
                step = 0.1
        elif c == ord('r'):
            pan=90
            tilt=90
            step=1.0
        send_udp_command(pan,tilt)


if __name__=="__main__":
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)

    myscreen = curses.initscr()
    myscreen.keypad(1)
    curses.noecho()
    curses.cbreak()
    myscreen.border(0)

    keyboard_controller(myscreen)

    myscreen.keypad(0)
    exit()
