ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

# "Activate" Python env
ENV VIRTUAL_ENV=/build/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ARG CONTAINER_USER="ebcl"

USER root

# add arm64 arch for cross-building
RUN dpkg --add-architecture arm64
RUN apt update
RUN apt -y install libc6:arm64

# install elbe dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt update
RUN apt -y install \
    openssh-server debootstrap reprepro python3 python3-pip python3-venv \
    binfmt-support qemu-user-static locales libparted-dev \
    cpio patchelf libgpgme-dev swig libvirt-dev python3-apt python3-parted \
    tmux dosfstools e2fsprogs xfsprogs file lsof vim busybox-static:arm64

# Prepare the elbe setup
RUN mkdir -p /var/cache/elbe
RUN mkdir -p /var/cache/elbe/installer
RUN mkdir -p /var/cache/elbe/devel
COPY config/elbe/source.xml /var/cache/elbe/

# allow SSH root login
RUN mkdir -p /etc/ssh
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

# fix permissions
RUN chown $CONTAINER_USER:$CONTAINER_USER /var/cache/elbe

# Get elbe
WORKDIR /var/cache/elbe/devel
RUN wget https://github.com/Elektrobit/elbe/archive/refs/heads/elbe_docker_container.zip
RUN unzip elbe_docker_container.zip
RUN rm -f elbe_docker_container.zip
RUN mv elbe-elbe_docker_container/* .
RUN rm -rf elbe-elbe_docker_container
RUN chown $CONTAINER_USER:$CONTAINER_USER /var/cache/elbe/devel

# Copy elbe helper scripts
COPY scripts/elbe/* /build/bin/
# Copy binfmt helper scripts
COPY scripts/binfmt/* /build/bin/

# Add elbe to PATH
USER root

# Enable binfmt for cross-building
RUN echo "sudo bash -c \"/build/bin/register_binfmt --reset -p yes\"" >> /home/$CONTAINER_USER/.bashrc
# Run the elbe service
RUN echo "start_elbe_service" >> /home/$CONTAINER_USER/.bashrc

USER $CONTAINER_USER

# Install elbe dependencies
# python-parted conflicts with pyparted (used by embdgen)
RUN bash -c "pip install gpg CherryPy lxml Mako passlib pycdlib python-debian suds libvirt-python Beaker spyne sqlalchemy"
RUN bash -c "pip install -e /var/cache/elbe/devel"

# init elbe db
# PYTHONPATH is hack to make python3-apt available in the venv. The package is not maintained on Pipy and only avalable as deb
RUN bash -c "source /build/venv/bin/activate; PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages/ elbe db init"

WORKDIR /workspace

# Set the entry point
ENTRYPOINT ["/build/bin/init"]
