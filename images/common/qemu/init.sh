#!/bin/sh

find_device_by_label() {
    LABEL_TO_FIND=$1
    LABEL_NAME=$(echo "$LABEL_TO_FIND" | cut -d '=' -f 2 )

    while read -r major minor blocks name; do

        if [ "$name" != "name" ]; then

            DEVICE="/dev/$name"

            if [ -b "$DEVICE" ]; then
                DEVICE_LABEL=$(e2label "$DEVICE" 2>/dev/null)

                if [ "$DEVICE_LABEL" = "$LABEL_NAME" ]; then
                    echo "$DEVICE"
                    return 0
                fi
            fi
        fi
    done < /proc/partitions
    echo "not_found_by_label"
    return 1
}


mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

cmdline=$(cat /proc/cmdline)
echo "Kernel commandline: ${cmdline}"

# Load kernel modules
which depmod
if [ $? -eq 0 ]; then
    depmod -a
fi

{% for mod in mods %}
modprobe {{ mod }}
{% endfor %}

{% if root %}
root={{ root }}
{% endif %}
init=/sbin/init

for param in $cmdline; do
    case $param in
        root=*)
            root=$(echo $param | cut -d'=' -f2-)
            echo "CMDLINE: root: ${root}"
            ;;
        init=*)
            init=$(echo $param | cut -d'=' -f2-)
            echo "CMDLINE: init: ${init}"
            ;;
    esac
done

# Handle LABEL and UUID
case $root in
    LABEL=*)
        root=$(find_device_by_label $root)
        echo "find_device_by_label returned $root"
        ;;
esac

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

echo "Using device $root as root filesystem."
mkdir -p /sysroot
mount -o rw $root /sysroot

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

mount --move /proc /sysroot/proc
mount --move /sys /sysroot/sys
mount --move /dev /sysroot/dev

mount -t tmpfs none /sysroot/tmp

mkdir -p /sysroot/dev/shm
mount -t tmpfs shmfs /sysroot/dev/shm

mount -t cgroup2 none /sysroot/sys/fs/cgroup

exec switch_root /sysroot /usr/sbin/init
