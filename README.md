# Servo controller for a pan tilt camera using a beaglebone black

pan_tilt_camera_server.py runs on the beaglebone black

pan_tilt_camera_client.py is used to send keyboard commands to the beaglebone

perplexity_controller.py listens to perplexity json messages over a tcp socket and sends commands to the beaglebone (using rost-cli)

TODO:

* clean up the code
* Add command line arguments
* Implement different controllers for the pan tilt servo

