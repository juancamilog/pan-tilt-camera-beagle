#!/usr/bin/env bash

id=$1

#/home/yogi/Projects/pan-tilt-camera-beagle/pan_tilt_camera_client.py --sunshine_port 9001 --pt_host mrldrifter2.local --tilt_min 35 --tilt_max 105 --pan_min 10 --pan_max 165 --decay_rate 0.5 --pan_kp 3.00 --tilt_kp -1.00

#/home/yogi/Projects/pan-tilt-camera-beagle/pan_tilt_camera_client.py --sunshine_port 9001 --pt_host mrldrifter2.local --tilt_min 75 --tilt_max 105 --pan_min 75 --pan_max 135 --decay_rate 0.0 --pan_kp 4.0 --pan_ki 0.8 --pan_kd 0.1 --tilt_kp -0.00
/home/yogi/Projects/pan-tilt-camera-beagle/pan_tilt_camera_client.py --sunshine_port 9001 --pt_host 132.206.74.167 --tilt_min 35 --tilt_max 105 --pan_min 10 --pan_max 165 --decay_rate 0.0 --pan_kp 4.0 --pan_ki 0.2 --pan_kd 0.1 --tilt_kp -4.00 --tilt_ki 0.1 --tilt_kd 0.1
