#!/bin/bash

# Startup script for macOS ARM64 drone control environment
# Usage: ./start_macos.sh [ros1|ros2]

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

echo "========================= macOS ARM64 Drone Configuration ========================="
echo "ROS Version: $ROS_VERSION"
echo "ROS Distro: $ROS_DISTRO"
echo "ROS Workspace: $ROS_WORKSPACE"
echo "=========================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if XQuartz is installed and running (for GUI support)
if ! pgrep -x "Xquartz" > /dev/null; then
    echo "Warning: XQuartz is not running. GUI applications may not work properly."
    echo "Please install and start XQuartz:"
    echo "1. Install XQuartz from https://www.xquartz.org/"
    echo "2. Start XQuartz"
    echo "3. Run: xhost +localhost"
    echo ""
    read -p "Continue without XQuartz? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "XQuartz is running. Enabling X11 forwarding..."
    xhost +localhost
    xhost +local:docker
fi

# Ensure X11 permissions are set correctly (before setting DISPLAY)
echo "Setting up X11 permissions..."
# Use the method from the GitHub gist for better compatibility
xhost +localhost
# Get hostname without .local suffix to avoid duplication
HOSTNAME=$(hostname | sed 's/\.local$//')
xhost +${HOSTNAME}.local

# Set display for Docker (after xhost commands)
# Use host.docker.internal:0 as recommended in the GitHub gist
export DISPLAY=host.docker.internal:0
echo "Using host.docker.internal:0 for X11 forwarding"

# Test X11 connection before starting the full environment
echo "Testing X11 connection..."
if command -v xeyes >/dev/null 2>&1; then
    echo "Testing with xeyes..."
    timeout 3 xeyes >/dev/null 2>&1 && echo "✅ X11 connection successful!" || echo "⚠️  X11 test failed, but continuing..."
else
    echo "⚠️  xeyes not found, skipping X11 test"
fi

# Create ros_logs directory if it doesn't exist
mkdir -p ./${ROS_WORKSPACE}/ros_logs

# Start the ARM64 drone control environment
echo "Starting ARM64 drone control environment..."
ROS_VERSION=$ROS_VERSION \
ROS_DISTRO=$ROS_DISTRO \
ROS_WORKSPACE=$ROS_WORKSPACE \
docker compose -f docker-compose.arm64.yml up

echo "ARM64 drone control environment stopped."

# Cleanup
echo "Cleaning up X11 permissions..."
xhost -localhost
