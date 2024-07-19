ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"

USER root

# install elbe dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt update
RUN apt -y install \
    python3 python3-pip python3-venv libparted-dev python3-dev pkg-config \
    mtools e2fsprogs cryptsetup-bin dosfstools fakeroot fdisk

USER $CONTAINER_USER

# Install embedgen
WORKDIR /build
RUN git clone --branch v0.1.0 https://github.com/Elektrobit/embdgen.git embdgen
WORKDIR /build/embdgen
RUN bash -c "source /build/venv/bin/activate; pip install -e embdgen-core"
RUN bash -c "source /build/venv/bin/activate; pip install -e embdgen-cominit"
RUN bash -c "source /build/venv/bin/activate; pip install -e embdgen-config-yaml"

WORKDIR /workspace

# Set the entry point
ENTRYPOINT ["/build/bin/init"]
