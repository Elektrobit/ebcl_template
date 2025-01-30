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
{% for mod in mods %}
modprobe {{ mod }}
{% endfor %}

# Mount root filesystem
## !LINKSTO refconfig.484dfd43-1763-48cc-a1a4-7108d636130d, 1
# !id swqts.rootfs.passing
# !status approved
# !version 1
# !shortdesc The standard reference image shall use rootfs provided in the kernel commandline.
# !description
# !    The standard reference image shall use rootfs provided in the kernel commandline.
# !testin  none
# !testexec
# !    <ul>
# !    <li>Run standard reference image with root parameter passed as device or label to the kernel </li>
# !    </ul>
# !testpasscrit The /proc/cmdline includes the "root="" proper value passed to the kernel

{% if root %}
root={{ root }}
{% endif %}
init=/sbin/init
verity_root_hash=""
verity_root_data=""
test_overlay=""

for param in $cmdline; do
    case $param in
        root=*)
            root=$(echo $param | cut -d'=' -f2-)
            echo "CMDLINE: root: ${root}"
            ;;
        verity_root_hash=*)
            verity_root_hash=$(echo $param | cut -d'=' -f2-)
            echo "CMDLINE: verity_root_hash: ${verity_root_hash}"
            ;;
        verity_root_data=*)
            verity_root_data=$(echo $param | cut -d'=' -f2-)
            echo "CMDLINE: verity_root_data: ${verity_root_data}"
            ;;
        init=*)
            init=$(echo $param | cut -d'=' -f2-)
            echo "CMDLINE: init: ${init}"
            ;;
        test_overlay=*)
            test_overlay=$(echo $param | cut -d'=' -f2-)
            echo "Using test_overlay ${test_overlay} from kernel cmdline."
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

read_only=1
for param in $cmdline; do
    if [[ $param == "rw" ]]; then
        read_only=0
    fi
done

if [ -z "$verity_root_data" ]; then
    echo "No verity data partition given!"
    /bin/sh
fi


stat $verity_root_data
if [ $? -ne 0 ]; then
    # List devices
    echo "Available devices:"
    ls -lah /dev/vd*
    ls -lah /dev/sd*
    ls -lah /dev/mmc*

    echo "Dm-verity data device not found! Dropping to shell."
    echo "You can continue booting by exiting this shell."
    /bin/sh
fi

if [ -z "$verity_root_hash" ]; then
    echo "No verity root hash given!"
    /bin/sh
fi

echo "Mounting dm-verity protected root partition ${root} using data from ${verity_root_data} and hash ${verity_root_hash}."

# !LINKSTO refconfig.25cf3f67-d923-4d1e-93ff-afa83002bcce, 2
veritysetup open $root verified-sysroot ${verity_root_data} ${verity_root_hash}

echo "Using device $root as read-only root."
mkdir -p /sysroot
mount -o ro /dev/mapper/verified-sysroot /sysroot

# Mount test overlay
if [ -n "$test_overlay" ]; then
    echo "Mounting test overlay ${test_overlay}."
    stat $test_overlay
    if [ $? -eq 0 ]; then
        echo "Mount test overlay from device ${test_overlay}"
        mkdir -p /test_overlay
        mount $test_overlay /test_overlay

        # Ensure overlayFS is available
        modprobe overlay
        # Overlay-mount test additions
        mount -t overlay overlay -olowerdir=/sysroot:/test_overlay /sysroot
    else
        echo "Test overlay device not found!"
    fi
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

exec switch_root /sysroot /usr/sbin/init
