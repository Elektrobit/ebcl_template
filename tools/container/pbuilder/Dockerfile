ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"

# "Activate" Python env
ENV VIRTUAL_ENV=/build/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER root

# Install Debian tools
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y \
    dh-make devscripts pbuilder

# Setup pbuilder
COPY conf/pbuilder/pbuilderrc /home/ebcl/.pbuilderrc
RUN sudo chown ebcl:ebcl /home/ebcl/.pbuilderrc && chmod +x /home/ebcl/.pbuilderrc

RUN mkdir -p /home/ebcl/.pbuilder/hooks/
COPY conf/pbuilder/G99apt_arch /home/ebcl/.pbuilder/hooks/G99apt_arch
RUN sudo chown ebcl:ebcl /home/ebcl/.pbuilder/hooks/* && chmod +x /home/ebcl/.pbuilder/hooks/*

# Use pbuilderrc also for root
RUN sudo ln -s /home/ebcl/.pbuilderrc /root/.pbuilderrc

# Copy Debian metadata helper scripts
COPY scripts/deb/* /build/bin/

# Copy packaging helper scripts
COPY scripts/pbuilder/* /build/bin/

# Ensure correct attributes for scripts
RUN chown -R $CONTAINER_USER:$CONTAINER_USER /build/bin && \
    chmod +x /build/bin/*

USER $CONTAINER_USER

# Create keyring for debootstrap
RUN gpg --no-default-keyring --keyring trustedkeys.gpg --import /etc/apt/trusted.gpg.d/elektrobit.gpg
RUN gpg --no-default-keyring --keyring trustedkeys.gpg --import /etc/apt/trusted.gpg.d/ubuntu-keyring-2018-archive.gpg

# Set the entry point
ENTRYPOINT ["/build/bin/init"]
