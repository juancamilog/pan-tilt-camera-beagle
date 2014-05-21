#!/usr/bin/env python2
import json
import socket
import operator
import time
import numpy as np
from pan_tilt_camera_controller import pan_tilt_camera_controller
import curses

class perplexity_controller(pan_tilt_camera_controller):
    def __init__(self,pan_tilt_host="192.168.0.101",pan_tilt_port=5005, curses_screen=None, perplexity_host="localhost", perplexity_port=9001, boredom_rate=0.1, ptype="topic_perplexity", use_max=False):

        super(perplexity_controller,self).__init__(pan_tilt_host,pan_tilt_port, curses_screen)

        self.tcp_sock = None
        self.tcp_host = perplexity_host
        self.tcp_port = int(perplexity_port)

        self.kp = np.array([5.0,5.0])
        self.ki = np.array([0,0])
        self.kd = np.array([0,0])

        self.previous_error = np.array([0,0])
        self.integral_error = np.array([0,0])
        self.curr_time = time.time()

        self.perplexity_threshold = 1.0
        self.boredom_rate = boredom_rate
        self.ptype = ptype
        self.use_max =use_max

    def connect(self):
        super(perplexity_controller,self).connect()
        if self.tcp_sock is not None:
            self.disconnect()

        self.tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.tcp_sock.connect((self.tcp_host,self.tcp_port))

    def disconnect(self):
        self.tcp_sock.close()
        self.tcp_sock = None
        super(perplexity_controller,self).disconnect()

    def get_max_perplexity_coords(self,perplexity_dict, ptype="topic_perplexity", image_width=640, image_height=480, hfov=90, vfov=90, normalized=True):
        rows = int(perplexity_dict['rows'])
        cols = int(perplexity_dict['cols'])
        N = rows*cols
        cell_width = image_width/cols
        cell_height = image_height/rows
         
        # get the maximum
        max_ind = N/2
        max_val = 1.0
        if self.use_max:
            if ptype == "both":
                combined_perplexity = np.array(perplexity_dict["topic_perplexity"]) * np.array(perplexity_dict["word_perplexity"])
                max_ind,max_val = max(enumerate(combined_perplexity), key=operator.itemgetter(1))
            else:
                max_ind,max_val = max(enumerate(perplexity_dict[ptype]), key=operator.itemgetter(1))
        else:
            if ptype == "both":
                combined_perplexity = np.array(perplexity_dict["topic_perplexity"]) * np.array(perplexity_dict["word_perplexity"])
                max_ind = np.random.choice(N,1,p=combined_perplexity/combined_perplexity.sum())[0]
                max_val = combined_perplexity[max_ind]
            else:
                perplexity_distribution = np.array(perplexity_dict[ptype])
                max_ind = np.random.choice(N,1,p=perplexity_distribution/perplexity_distribution.sum())[0]
                max_val = perplexity_distribution[max_ind]

        # convert the index to cell corrdinates
        c_x = max_ind%cols + 0.5 
        c_y = max_ind//cols + 0.5

        # convert the cell coordinates to a pixel coordiinate vector centered in the middle of the image
        p_x =  c_x*cell_height - image_width/2 
        p_y = -c_y*cell_width + image_height/2
        if normalized:
            p_x = p_x/image_width
            p_y = p_y/image_height

        return (p_x,p_y,max_val)

    def get_control(self,error):
        dt = time.time() - self.curr_time
        self.curr_time = time.time()
        de = error-self.previous_error
        self.previous_error=error
        self.integral_error += error*dt

        command = self.kp*error + self.ki*self.integral_error + self.kd*de/dt

        return command

    def run(self, pan_init=90.0, tilt_init=90.0):
        infile = self.tcp_sock.makefile()

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
            try:
                line = infile.readline()
                if not line: continue
                result = json.loads(line)
                max_perplexity_px = self.get_max_perplexity_coords(result,ptype=self.ptype)
                self.myscreen.addstr(14, 25, "Current perplexity threshold: %f"%(self.perplexity_threshold))
                self.myscreen.addstr(15, 25, "Perplexity of target point: %f"%(max_perplexity_px[2]))

                if max_perplexity_px[2] > self.perplexity_threshold:
                    self.perplexity_threshold = max_perplexity_px[2]*self.boredom_rate
                else:
                    self.perplexity_threshold *= self.boredom_rate
                    continue
            except ValueError:
                continue

            # the error is how far the max perxplexity coordinates are from the center of the image
            error = -np.array(max_perplexity_px[:2])
            control = self.get_control(error)

            if self.pan > self.pan_limits[1]:
                self.pan = self.pan_limits[1] - 2
            if self.pan < self.pan_limits[0]:
                self.pan = self.pan_limits[0] + 2
            if self.tilt > self.tilt_limits[1]:
                self.tilt = self.tilt_limits[1] - 2
            if self.tilt < self.tilt_limits[0]:
                self.tilt = self.tilt_limits[0] + 2

            self.pan += control[0]*self.pan_speed
            self.tilt += control[1]*self.tilt_speed

            self.send_pan_tilt_command(self.pan,self.tilt)

        self.disconnect()
        self.myscreen.clear()
        curses.flushinp()
        self.myscreen.nodelay(0)
        return (self.pan, self.tilt)
