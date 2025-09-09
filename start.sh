#!/bin/bash

# Startup script for physical drone control environment
# Usage: ./start_physical.sh [ros1|ros2]

set -e

# Default values
ROS_VERSION=${1:-ros1}

# Validate ROS version
if [[ "$ROS_VERSION" != "ros1" && "$ROS_VERSION" != "ros2" ]]; then
    echo "Error: ROS_VERSION must be 'ros1' or 'ros2'"
    echo "Usage: $0 [ros1|ros2]"
    exit 1
fi

# Set ROS distro based on version
if [[ "$ROS_VERSION" == "ros1" ]]; then
    ROS_DISTRO="noetic"
    ROS_WORKSPACE="ros1_workspace"
else
    ROS_DISTRO="humble"
    ROS_WORKSPACE="ros2_workspace"
fi

echo "========================= Physical Drone Configuration ========================="
echo "ROS Version: $ROS_VERSION"
echo "ROS Distro: $ROS_DISTRO"
echo "ROS Workspace: $ROS_WORKSPACE"
echo "=========================================================================="

# Enable X11 forwarding for Debian 12
echo "Enabling X11 forwarding..."
xhost +local:docker

# Start the physical drone control environment
echo "Starting physical drone control environment..."
ROS_VERSION=$ROS_VERSION \
ROS_DISTRO=$ROS_DISTRO \
ROS_WORKSPACE=$ROS_WORKSPACE \
docker compose up

echo "Physical drone control environment stopped."

# docker-compose up --build