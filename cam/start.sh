#!/bin/bash

set -e

MEDIAMTX_WORKSPACE="/home/wheatfox/Downloads/mediamtx_bin"
MEDIAMTX_PATH="$MEDIAMTX_WORKSPACE/mediamtx"
MEDIAMTX_CONFIG_PATH="$MEDIAMTX_WORKSPACE/mediamtx.yml" 

prepare() {
    echo "Preparing..."
    # clean existing mediamtx process
    pkill -f "$MEDIAMTX_PATH" || true
    # clean existing rpicam-vid process
    pkill -f "rpicam-vid" || true
    # clean existing ffmpeg process
    pkill -f "ffmpeg" || true

    $MEDIAMTX_PATH -c $MEDIAMTX_CONFIG_PATH > /dev/null 2>&1 &

    sleep 2
}

start() {
    echo "Starting..."
    rpicam-vid --timeout 0 --inline --vflip --width 640 --height 480 --framerate 20 -o - | \
    ffmpeg -re -f h264 -i - -vcodec copy -f rtsp rtsp://0.0.0.0:8554/mystream
}

stop() {
    echo "Stopping..."
    pkill -f "rpicam-vid" || true
    pkill -f "ffmpeg" || true
    pkill -f "$MEDIAMTX_PATH" || true
    # make sure mediamtx is stopped
    pkill -f mediamtx
}   

trap stop EXIT

prepare
start