ARG BASE_CONTAINER_NAME="ubuntu:22.04"
FROM $BASE_CONTAINER_NAME

ARG CONTAINER_USER="ebcl"

# TODO: sysroot scripts and template

# "Activate" Python env
ENV VIRTUAL_ENV=/build/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER root

# Copy berrymill config
RUN mkdir -p /etc/berrymill
COPY conf/berrymill/berrymill_local.conf /etc/berrymill
COPY conf/berrymill/berrymill.conf /etc/berrymill
COPY conf/kiwi/kiwi-boxed-plugin.yml /etc/berrymill
COPY conf/kiwi/kiwi.yml /etc

# Copy linux.elektrobit.com repo key
RUN mkdir -p /etc/berrymill/keyrings.d
RUN cp /etc/apt/trusted.gpg.d/elektrobit.gpg /etc/berrymill/keyrings.d/

USER $CONTAINER_USER
WORKDIR /build

# Install berrymill
RUN pip install kiwi kiwi-boxed-plugin
RUN pip install 'berrymill @ git+https://github.com/tomirgang/berrymill.git@59dbfd7d022681402ef5d4758e4e146411f1cad6'

# copy apt helper scripts
COPY scripts/apt/* /build/bin/

# copy berrymill helper scripts
COPY scripts/berrymill/* /build/bin/

# copy gpg helper scripts
COPY scripts/gpg/* /build/bin/

# copy kiwi helper scripts
COPY scripts/kiwi/* /build/bin/

# change work dir to workspace mount point
WORKDIR /workspace

# Set the entry point
ENTRYPOINT ["/build/bin/init"]
