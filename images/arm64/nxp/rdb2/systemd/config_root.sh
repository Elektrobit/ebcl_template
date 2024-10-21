#!/bin/sh

# Link systemd as init
if [ ! -e "./sbin/init"  ]; then
    ln -s /usr/lib/systemd/systemd ./sbin/init
else 
    echo "sbin/init already exists."
    ls -lah ./sbin/init
fi
