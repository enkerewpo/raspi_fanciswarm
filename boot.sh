#!/bin/bash

# Default configuration
DEFAULT_ROS_VERSION="ros1"
DEFAULT_ROS_DISTRO="noetic"
DEFAULT_ROS_WORKSPACE="ros1_workspace"
DEFAULT_COMMAND="/bin/bash"

if [[ "$(uname)" == "Darwin" ]]; then
    open -a XQuartz
    xhost + 127.0.0.1
    DISPLAY_ENV="-e DISPLAY=host.docker.internal:0"
    X11_SOCKET_MOUNT="-v /tmp/.X11-unix:/tmp/.X11-unix"
elif [[ "$(uname)" == "Linux" ]]; then
    # For Linux (including Debian 12), enable X11 forwarding
    xhost +local:docker
    DISPLAY_ENV="-e DISPLAY=$DISPLAY"
    X11_SOCKET_MOUNT="-v /tmp/.X11-unix:/tmp/.X11-unix:rw"
else
    DISPLAY_ENV=""
    X11_SOCKET_MOUNT=""
fi

# Parse command line arguments
ROS_VERSION=${ROS_VERSION:-$DEFAULT_ROS_VERSION}
ROS_DISTRO=${ROS_DISTRO:-$DEFAULT_ROS_DISTRO}
ROS_WORKSPACE=${ROS_WORKSPACE:-$DEFAULT_ROS_WORKSPACE}
COMMAND=${COMMAND:-$DEFAULT_COMMAND}

# Image and container names based on ROS version
IMAGE_NAME="${ROS_VERSION}-${ROS_DISTRO}-image"
CONTAINER_NAME="${ROS_VERSION}-${ROS_DISTRO}-container"

function show_config() {
    echo "========================= Current Configuration =========================="
    echo "ROS Version: $ROS_VERSION"
    echo "ROS Distro: $ROS_DISTRO"
    echo "ROS Workspace: $ROS_WORKSPACE"
    echo "Command: $COMMAND"
    echo "Image Name: $IMAGE_NAME"
    echo "Container Name: $CONTAINER_NAME"
    echo "=========================================================================="
}

function build_image() {
    echo "Building Docker image: $IMAGE_NAME..."
    echo "Using Dockerfile: Dockerfile.${ROS_VERSION}"
    sudo docker build -t $IMAGE_NAME -f Dockerfile.${ROS_VERSION} .
}

function start_container() {
    if [[ "$(uname)" == "Darwin" ]]; then
        if ! pgrep -xq -- "XQuartz"; then
            open -a XQuartz
            sleep 2
        fi
        xhost + 127.0.0.1
        DISPLAY_ENV="-e DISPLAY=host.docker.internal:0"
        X11_SOCKET_MOUNT="-v /tmp/.X11-unix:/tmp/.X11-unix"
    elif [[ "$(uname)" == "Linux" ]]; then
        # For Linux (including Debian 12), enable X11 forwarding
        xhost +local:docker
        DISPLAY_ENV="-e DISPLAY=$DISPLAY"
        X11_SOCKET_MOUNT="-v /tmp/.X11-unix:/tmp/.X11-unix:rw"
    else
        DISPLAY_ENV=""
        X11_SOCKET_MOUNT=""
    fi
    echo "Starting Docker container: $CONTAINER_NAME..."
    echo "Command: $COMMAND"
    sudo docker run -it --name $CONTAINER_NAME \
        --network host \
        -v $(pwd):/workspace \
        -v $(pwd)/${ROS_WORKSPACE}:/workspace/${ROS_WORKSPACE} \
        $X11_SOCKET_MOUNT \
        $DISPLAY_ENV \
        -e ROS_VERSION=$ROS_VERSION \
        -e ROS_DISTRO=$ROS_DISTRO \
        -e ROS_WORKSPACE=$ROS_WORKSPACE \
        --privileged \
        $IMAGE_NAME $COMMAND
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

function commit_container() {
    echo "Committing container changes to image: $CONTAINER_NAME -> $IMAGE_NAME..."
    sudo docker commit $CONTAINER_NAME $IMAGE_NAME
    echo "Container changes have been committed to image: $IMAGE_NAME"
}

function push_image() {
    echo "Pushing image to Docker Hub: $IMAGE_NAME..."
    echo "Note: Make sure you are logged in to Docker Hub (docker login)"
    sudo docker push $IMAGE_NAME
}

function docker_compose_up() {
    echo "Starting with docker-compose..."
    echo "Configuration: ROS_VERSION=$ROS_VERSION, COMMAND=$COMMAND"
    ROS_VERSION=$ROS_VERSION ROS_DISTRO=$ROS_DISTRO ROS_WORKSPACE=$ROS_WORKSPACE COMMAND=$COMMAND docker-compose up
}

function docker_compose_down() {
    echo "Stopping docker-compose services..."
    docker-compose down
}

function docker_compose_build() {
    echo "Building with docker-compose..."
    echo "Configuration: ROS_VERSION=$ROS_VERSION"
    ROS_VERSION=$ROS_VERSION ROS_DISTRO=$ROS_DISTRO ROS_WORKSPACE=$ROS_WORKSPACE docker-compose build
}

function help() {
    echo "Usage: $0 {build|start|exec|stop|remove|commit|push|compose-up|compose-down|compose-build|config} [options]"
    echo ""
    echo "Commands:"
    echo "  build         Build the Docker image"
    echo "  start         Create and start a new container"
    echo "  exec          Enter the running container"
    echo "  stop          Stop the running container"
    echo "  remove        Remove the stopped container"
    echo "  commit        Commit container changes back to image"
    echo "  push          Push image to Docker Hub"
    echo "  compose-up    Start with docker-compose"
    echo "  compose-down  Stop docker-compose services"
    echo "  compose-build Build with docker-compose"
    echo "  config        Show current configuration"
    echo ""
    echo "Environment Variables:"
    echo "  ROS_VERSION   ROS version (ros1|ros2) [default: $DEFAULT_ROS_VERSION]"
    echo "  ROS_DISTRO    ROS distro (noetic|humble) [default: $DEFAULT_ROS_DISTRO]"
    echo "  ROS_WORKSPACE Workspace directory [default: $DEFAULT_ROS_WORKSPACE]"
    echo "  COMMAND       Custom command to run [default: $DEFAULT_COMMAND]"
    echo ""
    echo "Examples:"
    echo "  # Start ROS1 Noetic with default settings"
    echo "  $0 start"
    echo ""
    echo "  # Start ROS2 Humble with custom command"
    echo "  ROS_VERSION=ros2 ROS_DISTRO=humble COMMAND='ros2 launch fcu_core fcu_core.launch' $0 start"
    echo ""
    echo "  # Use docker-compose with ROS2"
    echo "  ROS_VERSION=ros2 ROS_DISTRO=humble $0 compose-up"
    echo ""
    echo "  # Show current configuration"
    echo "  $0 config"
}

# Parse command line arguments
case "$1" in
    build)
        show_config
        build_image
        ;;
    start)
        show_config
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
    commit)
        commit_container
        ;;
    push)
        push_image
        ;;
    compose-up)
        show_config
        docker_compose_up
        ;;
    compose-down)
        docker_compose_down
        ;;
    compose-build)
        show_config
        docker_compose_build
        ;;
    config)
        show_config
        ;;
    *)
        help
        ;;
esac