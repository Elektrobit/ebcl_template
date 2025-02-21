#!/bin/sh

# Link systemd as init
ln -s /usr/lib/systemd/systemd /sbin/init

# Start ebcl VM
systemctl enable start-ebcl-1.service
