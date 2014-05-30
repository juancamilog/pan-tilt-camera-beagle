#!/usr/bin/env python2
import json
import socket
import operator
import time
import numpy as np
from pan_tilt_camera_controller import pan_tilt_camera_controller
import curses

class perplexity_controller(pan_tilt_camera_controller):
    def __init__(self,pan_tilt_host="192.168.0.101",pan_tilt_port=5005, curses_screen=None, perplexity_host="localhost", perplexity_port=9001, boredom_rate=0.1, ptype="topic_perplexity", use_max=False, pan_limits=[0,180], tilt_limits=[0,180], pan_gains = [5.0,0.0,0.0], tilt_gains = [-1.0,0.0,0.0]):

        super(perplexity_controller,self).__init__(pan_tilt_host,pan_tilt_port, curses_screen, pan_limits, tilt_limits)

        self.tcp_sock = None
        self.tcp_host = perplexity_host
        self.tcp_port = int(perplexity_port)

        self.kp = np.array([pan_gains[0],tilt_gains[0]])
        self.ki = np.array([pan_gains[1],tilt_gains[1]])
        self.kd = np.array([pan_gains[2],tilt_gains[2]])

        self.previous_error = np.array([0,0])
        self.integral_error = np.array([0,0])
        self.curr_time = time.time()

        self.perplexity_threshold = 1.0
        self.boredom_rate = boredom_rate
        self.ptype = ptype
        self.use_max =use_max

        self.target_smoothing = 0.85

        self.prev_p_x = 0.0
        self.prev_p_y = 0.0

        self.connected = False

    def connect(self):
        super(perplexity_controller,self).connect()
	if self.tcp_sock is not None:
	    self.disconnect()

	self.tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#self.tcp_sock.settimeout(5.0)
        try:
            self.tcp_sock.connect((self.tcp_host,self.tcp_port))
            self.connected = True
            return True
        except socket.error,e:
            return False

    def disconnect(self):
        self.tcp_sock.close()
        self.tcp_sock = None
        super(perplexity_controller,self).disconnect()

    def get_max_perplexity_coords(self,perplexity_dict, ptype="topic_perplexity", image_width=640, image_height=480, hfov=90, vfov=90, normalized=True, smoothing=False):
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
        p_x =  c_x*cell_height - image_width/2.0
        p_y = -c_y*cell_width + image_height/2.0
        if normalized:
            p_x = p_x/(image_width/2.0)
            p_y = p_y/(image_height/2.0)

        if smoothing:
            alpha = self.target_smoothing
            p_x = (1-alpha)*self.prev_p_x + alpha*p_x
            p_y = (1-alpha)*self.prev_p_y + alpha*p_y
            self.prev_p_x = p_x
            self.prev_p_y = p_y

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
        self.send_pan_tilt_command(self.pan,self.tilt)

        iters = 0

        while c != ord('q'):
            iters += 1
            self.myscreen.refresh()
            c = self.myscreen.getch()
            self.myscreen.addstr(12, 25, "Pan: %f Tilt: %f"%(self.pan,self.tilt))
            if not self.connected:      
                try:
                    self.tcp_sock.connect((self.tcp_host,self.tcp_port))
		    infile = self.tcp_sock.makefile()
                    self.connected = True
                    self.myscreen.addstr(14, 25,"Connected!                                    ")
		    self.pan = np.random.uniform(self.pan_limits[0], self.pan_limits[1])
		    self.tilt = np.random.uniform(self.tilt_limits[0], self.tilt_limits[1])
                    self.send_pan_tilt_command(self.pan,self.tilt)
                    time.sleep(1.0)
                    continue
                except socket.error,e:
                    self.myscreen.addstr(14, 25,"Lost connection, trying to reconnect...       ")
		    self.myscreen.addstr(15,25,"                                               ")
                    self.myscreen.addstr(15,25,str(e))
                    self.connected = False
                    time.sleep(1.0)
                    continue
            try:
                try:
                    line = infile.readline()
                  
                    if not line:
                        self.connected = False
                        self.myscreen.addstr(14, 25,"Lost connection, trying to reconnect...       ")
                        self.myscreen.addstr(15,25,"                                               ")
                        self.tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        #self.tcp_sock.settimeout(5.0)
                        time.sleep(1.0)
                        continue
                except socket.error,e:
                    self.connected = False
                    self.myscreen.addstr(14, 25,"Lost connection, trying to reconnect...       ")
                    self.myscreen.addstr(15,25,"                                               ")
                    self.myscreen.addstr(15,25,str(e))
		    self.tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		    #self.tcp_sock.settimeout(5.0)
		    time.sleep(1.0)
		    continue

                result = json.loads(line)
                max_perplexity_px = self.get_max_perplexity_coords(result,ptype=self.ptype)
                self.myscreen.addstr(14, 25, "Current perplexity threshold: %f"%(self.perplexity_threshold))
                self.myscreen.addstr(15,25,"                                               ")
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
                # hack!
                if self.pan > 180.0:
                    self.pan = 0.0
                    self.tilt = 180 - self.tilt
                else:
                    self.pan = self.pan_limits[1]
            if self.pan < self.pan_limits[0]:
                # hack!
                if self.pan < 0.0:
                    self.pan = 180.0
                    self.tilt = 180 - self.tilt
                else:
                    self.pan = self.pan_limits[0]
            if self.tilt > self.tilt_limits[1]:
                self.tilt = self.tilt_limits[1]
            if self.tilt < self.tilt_limits[0]:
                self.tilt = self.tilt_limits[0]


            self.pan += control[0]*self.pan_speed
            self.tilt += control[1]*self.tilt_speed
            
            if not self.send_pan_tilt_command(self.pan,self.tilt):
                self.myscreen.addstr(18,25,"Could not send command, camera might be offline")
            else: 
                self.myscreen.addstr(18,25,"CAMERA OK                                       ")
                

        self.disconnect()
        self.myscreen.clear()
        curses.flushinp()
        self.myscreen.nodelay(0)
        return (self.pan, self.tilt)
