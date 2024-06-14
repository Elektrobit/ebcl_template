ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"

USER root

# install elbe dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt update
RUN apt -y install libjsoncpp-dev

USER $CONTAINER_USER
WORKDIR /build

# add cmake toolchains
RUN mkdir -p /build/cmake
COPY conf/cmake/* /build/cmake/

# add cmake helper scripts
COPY scripts/cmake/* /build/bin/

# Result folder for cmake builds
RUN mkdir -p /build/results/apps

# change work dir to workspace mount point
WORKDIR /workspace

# Set the entry point
ENTRYPOINT ["/build/bin/init"]
