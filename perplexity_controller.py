#!/usr/bin/env python2
import json
import socket
import operator
import time
import numpy as np

class perplexity_controller:
    def __init__(self,perplexity_host="localhost", perplexity_port=9001,pan_tilt_host="192.168.0.101",pan_tilt_port=5005, boredom_rate=0.1, ptype="topic_perplexity", use_max=False):
        self.tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.udp_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        self.tcp_host = perplexity_host
        self.tcp_port = perplexity_port
        self.udp_host = pan_tilt_host
        self.udp_port = pan_tilt_port

        self.current_pan = 90
        self.current_tilt = 90

        self.kp = np.array([20.0,20.0])
        self.ki = np.array([0,0])
        self.kd = np.array([0,0])

        self.previous_error = np.array([0,0])
        self.integral_error = np.array([0,0])
        self.curr_time = time.time()

        self.pan = 90
        self.tilt = 90

        self.perplexity_threshold = 1.0
        self.boredom_rate = boredom_rate
        self.ptype = ptype
        self.use_max =use_max


    def connect(self):
        self.tcp_sock.connect((self.tcp_host,self.tcp_port))
        self.udp_sock.connect((self.udp_host,self.udp_port))

    def disconnect(self):
        self.tcp_sock.close()
        self.udp_sock.close()

    def send_pan_tilt_command(self,pan,tilt):
        msg = str(pan)+','+str(tilt)
        self.udp_sock.sendto(msg, (self.udp_host, self.udp_port))

    def get_max_perplexity_coords(self,perplexity_dict, ptype="topic_perplexity", image_width=640, image_height=480, normalized=True):
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
                combined_perplexity = np.array(perplexity_dict["topic_perplexity"]) + np.array(perplexity_dict["word_perplexity"])
                max_ind,max_val = max(enumerate(combined_perplexity), key=operator.itemgetter(1))
            else:
                max_ind,max_val = max(enumerate(perplexity_dict[ptype]), key=operator.itemgetter(1))
        else:
            if ptype == "both":
                combined_perplexity = np.array(perplexity_dict["topic_perplexity"]) + np.array(perplexity_dict["word_perplexity"])
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

    def run(self):
        infile = self.tcp_sock.makefile()
        while True:
            try:
                line = infile.readline()
                if not line: continue
                result = json.loads(line)
                max_perplexity_px = self.get_max_perplexity_coords(result,ptype=self.ptype)
                print "------------------------------------"
                print "Current perplexity threshold: %f"%(self.perplexity_threshold)
                print "Perplexity of target point: %f"%(max_perplexity_px[2])

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

            self.pan += control[0]
            if self.pan > 180:
                self.pan = 178
            if self.pan < 0:
                self.pan = 2
            if self.tilt > 180:
                self.tilt = 178
            if self.tilt < 0:
                self.tilt = 2

            self.tilt += control[1]
            self.send_pan_tilt_command(self.pan,self.tilt)

            print "Camera pose is now: pan %f, tilt %f"%(self.pan,self.tilt)
            

if __name__=="__main__":
    controller = perplexity_controller(perplexity_host="localhost", perplexity_port=9001,pan_tilt_host="192.168.0.101",pan_tilt_port=5005, boredom_rate=0.9, ptype="topic_perplexity", use_max=True)
    try:
        controller.connect()
        controller.run()
    except Exception,e:
        controller.disconnect()
