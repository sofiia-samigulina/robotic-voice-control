#!/bin/bash

xhost +

docker run -it \
--gpus all \
--runtime=nvidia \
--net=host \
--env="DISPLAY" \
--env="QT_X11_NO_MITSHM=1" \
--env="NO_AT_BRIDGE=1" \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v ~/temp:/root/temp \
-v /dev/v4l:/dev/v4l \
-v /dev/bus/usb:/dev/bus/usb \
--device=/dev/myserial \
--device=/dev/ydlidar \
--device=/dev/rplidar \
--device=/dev/astro_pro_plus \
--device=/dev/astro_pro_plus_rgb \
--device=/dev/input \
--device=/dev/snd \
--device=/dev/video0 \
--device=/dev/video1 \
--device=/dev/video2 \
--device=/dev/video3 \
--device=/dev/camera_depth \
-v ~/Sofiia/shared:/root/data/shared \
--name=voice_ctrl_sofiia \
-p 9090:9090 \
-p 8888:8888 \
yahboomtechnology/ros-noetic:3.0.4 /bin/bash
