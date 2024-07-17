ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

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
    binfmt-support qemu-user-static locales python3-cherrypy3 \
    python3-gpg python3-lxml python3-mako python3-passlib python3-pycdlib \
    python3-debian python3-suds python3-libvirt swig cpio patchelf \
    python3-beaker python3-spyne python3-sqlalchemy python3-parted \
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

# init elbe db
RUN PATH=$PATH:/var/cache/elbe/devel PYTHONPATH=$PYTHONPATH:/var/cache/elbe/devel elbe db init

# Copy elbe helper scripts
COPY scripts/elbe/* /build/bin/
# Copy binfmt helper scripts
COPY scripts/binfmt/* /build/bin/

# Add elbe to PATH
USER root
RUN echo "export PATH=\$PATH:/var/cache/elbe/devel" >> /home/$CONTAINER_USER/.bashrc
RUN echo "PYTHONPATH=\$PYTHONPATH:/var/cache/elbe/devel" >> /home/$CONTAINER_USER/.bashrc
RUN echo "export PATH=\$PATH:/var/cache/elbe/devel" >> /root/.bashrc
RUN echo "PYTHONPATH=\$PYTHONPATH:/var/cache/elbe/devel" >> /root/.bashrc

# Enable binfmt for cross-building
RUN echo "sudo /build/bin/register_binfmt --reset -p yes" >> /home/$CONTAINER_USER/.bashrc
# Run the elbe service
RUN echo "start_elbe_service" >> /home/$CONTAINER_USER/.bashrc

USER $CONTAINER_USER

# Installation folders for SDKs
RUN mkdir -p /build/sdks

WORKDIR /workspace

# Set the entry point
ENTRYPOINT ["/build/bin/init"]