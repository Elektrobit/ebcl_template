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
echo "Using root ${root}."
mount $root /sysroot

# Switch to the new root filesystem
exec switch_root /sysroot /sbin/init
