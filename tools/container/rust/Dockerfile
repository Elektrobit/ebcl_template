ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"

USER root

# Setup rust including aarch64 toolchain
ENV DEBIAN_FRONTEND noninteractive
RUN apt update
RUN apt -y install rustc cargo
ENV PATH="/home/$CONTAINER_USER/.cargo/bin:${PATH}"

# Add rust binaries to PATH
RUN echo "export PATH=\$PATH:~/.cargo/bin" >> /home/$CONTAINER_USER/.bashrc
RUN echo "export PATH=\$PATH:/home/$CONTAINER_USER/.cargo/bin" >> /root/.bashrc

USER $CONTAINER_USER

# Set the entry point
ENTRYPOINT ["/build/bin/init"]