#!/bin/bash

IMAGE_NAME="ros1-noetic-tools"
CONTAINER_NAME="ros1-noetic"

function build_image() {
    echo "Building Docker image: $IMAGE_NAME..."
    sudo docker build -t $IMAGE_NAME .
}

function start_container() {
    echo "Starting Docker container: $CONTAINER_NAME..."
    sudo docker run -it --name $CONTAINER_NAME --network host -v $(pwd):/workspace $IMAGE_NAME
}

function exec_container() {
    echo "Entering running container: $CONTAINER_NAME..."
    sudo docker exec -it $CONTAINER_NAME /bin/bash
}

function stop_container() {
    echo "Stopping container: $CONTAINER_NAME..."
    sudo docker stop $CONTAINER_NAME
}

function remove_container() {
    echo "Removing container: $CONTAINER_NAME..."
    sudo docker rm $CONTAINER_NAME
}

function help() {
    echo "Usage: $0 {build|start|exec|stop|remove}"
    echo ""
    echo "Commands:"
    echo "  build    Build the Docker image"
    echo "  start    Create and start a new container"
    echo "  exec     Enter the running container"
    echo "  stop     Stop the running container"
    echo "  remove   Remove the stopped container"
}

case "$1" in
    build)
        build_image
        ;;
    start)
        start_container
        ;;
    exec)
        exec_container
        ;;
    stop)
        stop_container
        ;;
    remove)
        remove_container
        ;;
    *)
        help
        ;;
esac