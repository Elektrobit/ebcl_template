#!/bin/sh

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

COMMANDLINE = $(cat /proc/cmdline)
echo "Kernel commandline: ${COMMANDLINE}"

# Load kernel modules
{% for mod in mods %}
modprobe {{ mod }}
{% endfor %}

# Mount root filesystem
root={{ root }}
for param in $COMMANDLINE; do
    if [[ $param == "root="* ]]; then
        root=${param:5}
    fi
done

stat $root
if [ $? -ne 0 ]; then
    # List devices
    echo "Available devices:"
    ls -lah /dev/vd*
    ls -lah /dev/sd*
    ls -lah /dev/mmc*

    echo "Root device not found! Dropping to shell."
    /bin/sh
fi

# TODO: handle ro / rw
# TODO: handle LABEL
echo "Using root ${root}."
mount $root /sysroot

# TODO: drop to shell if init is missing or not executable
# TODO: eval init kernel commandline parameter
# Switch to the new root filesystem
exec switch_root /sysroot /sbin/init
