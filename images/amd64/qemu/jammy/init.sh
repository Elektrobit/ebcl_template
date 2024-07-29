#!/bin/sh

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

# Load kernel modules
{% for mod in mods %}
modprobe {{ mod }}
{% endfor %}

# Mount root filesystem
root={{root}}
for param in $(cat /proc/cmdline); do
    if [[ $param == "root="* ]]; then
        root=${param:5}
    fi
done

stat $root
if [ $? -ne 0 ]; then
    # List devices
    echo "Available VDA devices:"
    ls -lah /dev/vda*

    echo "Root device not found! Dropping to shell."
    /bin/sh
fi

echo "Using root ${root}."
mount $root /sysroot

# Switch to the new root filesystem
exec switch_root /sysroot /sbin/init
