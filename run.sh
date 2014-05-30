#!/usr/bin/env bash


pid=0
pt_pid=0
trap cleanup SIGINT SIGTERM

cleanup()
{
  echo killing ${pid}
  kill -s SIGTERM $pid
  killall -9 screen
  #echo killing ${pt_pid}
  #kill -s SIGTERM $pt_pid
  exit 0
}

id=$1
while true
do

    #screen -d -m /home/yogi/Projects/pan-tilt-camera-beagle/pan_tilt_camera_client.py --pt_host 192.168.0.${id} --tilt_min 150 --decay_rate 0.5
    #pt_pid=$!
#    a=$(( RANDOM % 100 ))
#    echo a
#    if [ $(( a > 80 )) == 1 ]; then
#	id=102
#    else
#	id=101
#    fi

    d=`date "+cam${id}-%Y-%m-%d-%H-%M-%S"`
    mkdir $d
    pushd $d	
    header="Sunshine [ Entrance ]"
    footer="Yogesh Girdhar, Juan Camilo Gamboa, Travis Manderson, Greg Dudek"
    #footer=" "
    if [ $id == 102 ] ; then
	header="Sunshine [ Floating Cube ]"
    fi
    sunshine --mjpgstream=192.168.0.${id} --save-imgs --cell.space=32 --beta=0.5 --threads=8 --fullscreen --footer="${footer}" --header="$header" --broadcaster.port=9${id}&
    pid=$!
    sleep 3600
    echo "Killing"
    killall -9 screen
    kill ${pid}
    wait ${pid}
    #kill ${pt_pid}
    #wait ${pt_pid}
    popd
done
