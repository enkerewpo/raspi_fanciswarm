# we are on raspi so we have to use aarch64 ROS environment - wheatfox
FROM arm64v8/ros:noetic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    vim \
    net-tools \
    iputils-ping \
    curl \
    python3-pip \
    sudo \
    locales \
    cmake \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc

RUN apt-get update && apt-get install -y python3-rosdep && \
    rosdep init || true && \
    rosdep update && \
    apt-get install -y ros-noetic-serial ros-noetic-image-transport ros-noetic-tf

# Create shared workspace directory
RUN mkdir -p /workspace

# Set working directory to shared workspace
WORKDIR /workspace

# Define volume for workspace sharing
VOLUME ["/workspace"]

CMD ["/bin/bash"]
