#!/bin/sh

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

cmdline=$(cat /proc/cmdline)
echo "Kernel commandline: ${cmdline}"

# Load kernel modules
{% for mod in mods %}
modprobe {{ mod }}
{% endfor %}

# Mount root filesystem
root={{ root }}
for param in $cmdline; do
    if [[ $param == "root="* ]]; then
        root=${param:5}
    fi
done

# Handle LABEL and UUID
if [[ $root == "LABEL="* ]] || [[ $root == "UUID="* ]]; then
    $dev=$(findfs $root)
    if [ $? -ne 0 ]; then
        echo "No partition found for ${root}! Dropping to shell."
        /bin/sh
    else
        echo "Found device $dev for $root"
        $root=$dev
    fi
fi

init=/sbin/init
for param in $cmdline; do
    if [[ $param == "init="* ]]; then
        init=${param:5}
        echo "Using $init as init."
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
    echo "You can continue booting by exiting this shell."
    /bin/sh
fi

read_only=1
for param in $cmdline; do
    if [[ $param == "rw" ]]; then
        read_only=0
    fi
done

if [ $read_only -ne 1 ]; then
    echo "Using root $root writable."
    mount $root /sysroot

    # Ensure proc sys and dev exists
    mkdir -p /sysroot/proc
    mkdir -p /sysroot/sys
    mkdir -p /sysroot/dev
else
    echo "Using device $root as read-only root."
    mount -o ro $root /sysroot
fi

# Check if init exists
init_ok=0
if [ -L "/sysroot${init}" ]; then
    echo "${init} is a symlink."
    ls -lah "/sysroot${init}"
    init_ok=1
elif [ -f "/sysroot${init}" ]; then
    echo "${init} is a file..."
    if [ ! -x "/sysroot${init}" ]; then
        echo "${init} is not executable!"
    else
        init_ok=1
    fi
fi


# Switch to the new root filesystem
if [ $init_ok -ne 1 ]; then
    echo "There seems to be an issue with ${init}! Dropping to shell."
    echo "You can continue booting by exiting this shell."
    /bin/sh
fi 

exec switch_root /sysroot /sbin/init
