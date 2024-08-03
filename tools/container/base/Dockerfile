ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"
ARG HOST_USER=1000
ARG HOST_GROUP=1000

# Config apt sources
RUN mkdir -p /etc/apt/sources.list.d
COPY conf/apt/* /etc/apt/sources.list.d/
RUN rm -rf /etc/apt/sources.list && \
    touch /etc/apt/sources.list

# Copy linux.elektrobit.com repo key
RUN mkdir -p /etc/apt/trusted.gpg.d
COPY conf/apt-keys/elektrobit.gpg /etc/apt/trusted.gpg.d/

# Update container
RUN apt update
# Install compiler and base tools
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y \
    build-essential gcc g++ cmake pkg-config gdb-multiarch \
    gcc-aarch64-linux-gnu g++-aarch64-linux-gnu crossbuild-essential-arm64 \
    locales kmod curl wget xz-utils sudo git vim rsync file \
    python3 python3-pip python3-venv \
    lshw gdisk fdisk parted fakechroot fakeroot bmap-tools \ 
    tcpdump iputils-ping iproute2 iptables \
    qemu-system-arm qemu-system-x86 qemu-kvm

 # Setup locale
RUN export LC_ALL=en_US.UTF-8 && \
    export LANG=en_US.UTF-8 && \
    locale-gen en_US.UTF-8

# Create build user mathching outside UID and GID to avoid ownership issues
# and allow user to use sudo
RUN addgroup --gid $HOST_GROUP $CONTAINER_USER && \
  useradd -rm -d /home/$CONTAINER_USER -s /bin/bash -g $CONTAINER_USER -G sudo -u $HOST_USER $CONTAINER_USER && \
  echo "$CONTAINER_USER ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && \
  mkdir -p /home/$CONTAINER_USER/.ssh && \
  chown -R $CONTAINER_USER:$CONTAINER_USER /home/$CONTAINER_USER

# Prepare base structure
RUN mkdir -p /build/results/images && \
    mkdir -p results/packages && \
    mkdir -p images && \
    mkdir -p identity && \
    mkdir -p bin && \
    chown -R $CONTAINER_USER:$CONTAINER_USER /build
RUN mkdir -p /workspace && \
    chown -R $CONTAINER_USER:$CONTAINER_USER /workspace

# Create mount point for SSH keys
RUN mkdir -p /home/$CONTAINER_USER/.ssh && \
    chown -R $CONTAINER_USER:$CONTAINER_USER /home/$CONTAINER_USER

# Copy bashrc
COPY conf/bash/bashrc /home/$CONTAINER_USER/.bashrc
RUN chown -R $CONTAINER_USER:$CONTAINER_USER /home/$CONTAINER_USER && \
    chmod +x /home/$CONTAINER_USER/.bashrc

RUN mkdir -p /root
COPY conf/bash/bashrc /root/.bashrc
RUN chown -R root:root /root && \
    chmod +x /root/.bashrc

# Copy environment helper scripts
COPY scripts/bash/* /build/bin/

# Copy GnuPG helper scripts
COPY scripts/gpg/* /build/bin/

# Copy QEMU helper scripts
COPY scripts/qemu/* /build/bin/

# Copy mount helper scripts
COPY scripts/mount/* /build/bin/

# Ensure correct attributes for scripts
RUN chown -R $CONTAINER_USER:$CONTAINER_USER /build/bin && \
    chmod +x /build/bin/*

# Write version
RUN echo "1.2" > /etc/sdk_version

USER $CONTAINER_USER

# Prepare Python env
ENV VIRTUAL_ENV=/build/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install mypy pep8 pylint pytest pytest-cov robotframework

# Ensure venv owner
USER root
RUN chown -R $CONTAINER_USER:$CONTAINER_USER /build/venv

USER $CONTAINER_USER

# change work dir to workspace mount point
WORKDIR /workspace

# Set the entry point
ENTRYPOINT ["/build/bin/init"]
