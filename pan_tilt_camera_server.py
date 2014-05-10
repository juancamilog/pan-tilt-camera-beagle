#!/usr/bin/env python2
import Adafruit_BBIO.PWM as pwm
import socket
import signal

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
pan_servo_pin = "P9_16"
tilt_servo_pin = "P8_19"
freq = 75.0
tilt_duty_min = (6e-4)/(1.0/freq)*100.0
tilt_duty_max = (1.95e-3)/(1.0/freq)*100.0
tilt_duty_span = tilt_duty_max - tilt_duty_min
pan_duty_min = (5.25e-4)/(1.0/freq)*100.0
pan_duty_max = (2.35e-3)/(1.0/freq)*100.0
pan_duty_span = pan_duty_max - pan_duty_min

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
original_sigterm = signal.getsignal(signal.SIGTERM)
original_sigabrt = signal.getsignal(signal.SIGABRT)
original_sigint = signal.getsignal(signal.SIGINT)

def run():
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print ">>> Received message: >"+data+'<'
        dataArray = data.split(',');
        pan = float(dataArray[0])
        tilt = float(dataArray[1])
        print ">>> Setting new pose..."
        set_camera_pan(pan)
        set_camera_tilt(tilt)
        print ">>> The new pose of the camera is (%f,%f)"%(pan,tilt)

def set_camera_pan(angle=90.0):
    global pan_duty_min
    global pan_duty_span
    global pan_servo_pin
  
    angle_f = float(angle)
    duty = ((angle_f / 180.0) * pan_duty_span + pan_duty_min) 
    pwm.set_duty_cycle(pan_servo_pin, duty)
    
def set_camera_tilt(angle=90.0):
    global tilt_duty_min
    global tilt_duty_span
    global tilt_servo_pin
  
    angle_f = float(angle)
    duty = ((angle_f / 180.0) * tilt_duty_span + tilt_duty_min) 
    pwm.set_duty_cycle(tilt_servo_pin, duty)

def exit_gracefully(signum, frame):
    global pan_servo_pin
    global tilt_servo_pin
    global original_sigterm
    global original_sigabrt
    global original_sigint

    signal.signal(signal.SIGTERM, original_sigterm)
    signal.signal(signal.SIGABRT, original_sigabrt)
    signal.signal(signal.SIGINT, original_sigint)

    pwm.stop(pan_servo_pin)
    pwm.stop(tilt_servo_pin)
    pwm.cleanup()

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGABRT, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)    

if __name__ == '__main__':
    original_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, exit_gracefully)
    original_sigabrt = signal.getsignal(signal.SIGABRT)
    signal.signal(signal.SIGABRT, exit_gracefully)
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    pwm.start(pan_servo_pin, pan_duty_min + 0.5*pan_duty_span, freq)
    pwm.start(tilt_servo_pin, tilt_duty_min + 0.5*tilt_duty_span, freq)

    sock.bind((UDP_IP, UDP_PORT))
    try:
        run()
    except KeyboardInterrupt:
        pwm.stop(pan_servo_pin)
        pwm.stop(tilt_servo_pin)
        pwm.cleanup()
