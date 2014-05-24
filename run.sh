#!/usr/bin/env bash


pid=0
pt_pid=0
trap cleanup SIGINT SIGTERM

cleanup()
{
  echo killing ${pid}
  kill -s SIGTERM $pid
  killall screen
  #echo killing ${pt_pid}
  #kill -s SIGTERM $pt_pid
  exit 0
}

id=$1
while true
do
    d=`date "+cam${id}-%Y-%m-%d-%H-%M-%S"`
    mkdir $d
    pushd $d
    screen -d -m /home/yogi/Projects/pan-tilt-camera-beagle/pan_tilt_camera_client.py --pt_host 192.168.0.${id} --tilt_min 150 --decay_rate 0.5 &
    #pt_pid=$!
    sunshine --mjpgstream=192.168.0.${id} --save-imgs --cell.space=32 --beta=0.5 --threads=5 --fullscreen &
    pid=$!
    sleep 300
    echo "Killing"
    killall screen
    kill ${pid}
    wait ${pid}
    #kill ${pt_pid}
    #wait ${pt_pid}
    popd
done
