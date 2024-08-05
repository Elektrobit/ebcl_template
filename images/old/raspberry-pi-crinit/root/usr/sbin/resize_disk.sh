#!/usr/bin/sh

if [ -f "/etc/firstboot" ]; then
    echo "resizing disk ..."
    growpart /dev/mmcblk0 2
    resize2fs /dev/mmcblk0p2
    rm /etc/firstboot
fi
