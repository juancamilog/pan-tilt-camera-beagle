# Servo controller for a pan tilt camera using a beaglebone black

pan_tilt_camera_server.py runs on the beaglebone black

pan_tilt_camera_client.py is used to send keyboard commands to the beaglebone

perplexity_controller.py listens to perplexity json messages over a tcp socket and sends commands to the beaglebone (using rost-cli)


## Example

First, compile rost-cli (requires OpenCV 2.4.X) and  run sunshine
    cd <PATH_TO_ROST_CLI>/bin
    ./sunshine --camera 0 --cell.space=32 --threads=6 --broadcaster.port=9001

Then, run the perplexity controller
    cd <PATH_TO_THIS_REPO>
    ./pan_tilt_camera_client.py --sunshine_port 9001 --pt_host localhost --pt_port 9003 --decay_rate 0.1 --pan_kp 4.0 --pan_ki 0.2 --pan_kd 0.1 --tilt_kp -4.00 --tilt_ki 0.1 --tilt_kd 0.1 --pan 90 --tilt 90

Run `./pan_tilt_camera_client --help` for a description of the arguments.


