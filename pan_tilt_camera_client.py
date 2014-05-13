#!/usr/bin/env python
import curses
import signal

from keyboard_controller import keyboard_controller
from perplexity_controller import perplexity_controller

def exit_gracefully(signum, frame):
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

def main_loop(pan_tilt_host, pan_tilt_port, perplexity_host, perplexity_port, boredom_rate, use_max):
    step = 1.0
    pan  = 90.0
    tilt = 90.0

    k_controller = keyboard_controller(pan_tilt_host, pan_tilt_port, myscreen)
    tp_controller = perplexity_controller(pan_tilt_host, pan_tilt_port, myscreen, perplexity_host, perplexity_port, boredom_rate, "topic_perplexity", use_max)
    wp_controller = perplexity_controller(pan_tilt_host, pan_tilt_port, myscreen, perplexity_host, perplexity_port, boredom_rate, "word_perplexity", use_max)
    mp_controller = perplexity_controller(pan_tilt_host, pan_tilt_port, myscreen, perplexity_host, perplexity_port, boredom_rate, "both", use_max)

    c = ''
    while c != ord('q'):
        myscreen.refresh()
        myscreen.addstr(3, 5, "Press 'k' for keyboard control")
        myscreen.addstr(4, 5, "Press 't' for topic perplexity control")
        myscreen.addstr(5, 5, "Press 'w' for word perplexity control")
        myscreen.addstr(6, 5, "Press 'm' for topic+word perplexity control")
        myscreen.addstr(7, 5, "Press 'q' to exit.")
        myscreen.border(0)
        c = myscreen.getch()

        if c == ord('k'):
            k_controller.connect()
            (pan,tilt) = k_controller.run(pan,tilt)
        elif c == ord('t'):
            tp_controller.connect()
            (pan,tilt) = tp_controller.run(pan,tilt)
        elif c == ord('w'):
            wp_controller.connect()
            (pan,tilt) = wp_controller.run(pan,tilt)
        elif c == ord('m'):
            wp_controller.connect()
            (pan,tilt) = wp_controller.run(pan,tilt)

if __name__=="__main__":
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)

    myscreen = curses.initscr()
    myscreen.keypad(1)
    curses.noecho()
    curses.cbreak()

    main_loop("192.168.0.101","5005","localhost", "9001", 0.9, True)

    myscreen.keypad(0)
    exit()
