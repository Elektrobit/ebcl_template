ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"

USER $CONTAINER_USER

# Setup rust including aarch64 toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y
ENV PATH="/home/$CONTAINER_USER/.cargo/bin:${PATH}"
RUN rustup target add aarch64-unknown-linux-gnu

# Add rust binaries to PATH
USER root
RUN echo "PATH=$PATH:~/.cargo/bin" >> /home/$CONTAINER_USER/.bashrc
RUN echo "PATH=$PATH:/home/$CONTAINER_USER/.cargo/bin" >> /root/.bashrc

USER $CONTAINER_USER

# Set the entry point
ENTRYPOINT ["/build/bin/init"]