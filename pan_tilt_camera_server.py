#!/usr/bin/env python2
import Adafruit_BBIO.PWM as pwm
import atexit
import socket


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

sock = socket.socket(socket.AF_INET,     # Internet
                     socket.SOCK_DGRAM)  # UDP


def run():
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print ">>> Received message: >"+data+'<'
        dataArray = data.split(',')
        pan = float(dataArray[0])
        tilt = float(dataArray[1])
        print ">>> Setting new pose..."
        set_camera_pan(pan)
        set_camera_tilt(tilt)
        msg = ">>> The new pose of the camera is (%f,%f)"
        print msg % (pan, tilt)


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

    pwm.stop(pan_servo_pin)
    pwm.stop(tilt_servo_pin)
    pwm.cleanup()


if __name__ == '__main__':
    atexit.register(exit_gracefully)

    pwm.start(pan_servo_pin, pan_duty_min + 0.5*pan_duty_span, freq)
    pwm.start(tilt_servo_pin, tilt_duty_min + 0.5*tilt_duty_span, freq)

    sock.bind((UDP_IP, UDP_PORT))
    try:
        run()
    except KeyboardInterrupt:
        pwm.stop(pan_servo_pin)
        pwm.stop(tilt_servo_pin)
        pwm.cleanup()
