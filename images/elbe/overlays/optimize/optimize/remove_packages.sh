#!/bin/sh

echo "Adding busybox tools ..."
mkdir -p /optimize/bin
busybox --install /optimize/bin
export PATH=$PATH:/optimize/bin

echo "Removing not needed packages ..."
packages=$( cat /optimize/packages.txt | tr '\n' ' ')
dpkg --purge --force-all $packages || true

# delete left-overs from packages
echo "Deleting left-overs of removed packages ..."
for package in $packages; do
    hashes="/var/lib/dpkg/info/${package}.md5sums"
    if [ -f $hashes ]; then
        echo "Deleting left-overs of $package ..."
        for file in $(echo $hash | awk '{ print $2 }'); do
            path="/${file}"
            if [ -f $path ]; then
                echo "Deleting $path."
                rm -f $path
            fi
        done
    else
        echo "No md5sums for ${package}."
    fi

    list="/var/lib/dpkg/info/${package}.list"
    if [ -f $list ]; then
        echo "Deleting generated files of $package ..."
        for file in $(cat $list); do
            if [ -f $file ]; then
                echo "Deleting $file ..."
                rm -f $file
            fi
        done
    else
        echo "No list for ${package}."
    fi

    echo "Deleting package scripts of  $package ..."
    rm -f "/var/lib/dpkg/info/${package}.preinst"
    rm -f "/var/lib/dpkg/info/${package}.prerm"
    rm -f "/var/lib/dpkg/info/${package}.postinst"
    rm -f "/var/lib/dpkg/info/${package}.postrm"

    echo "Deleting documentation of $package ..."
    rm -rf "usr/share/doc/${package}"
done

# Delete broken symlinks
echo "Deleting broken symlinks ..."
find / -not -path "/proc*" -type l ! -exec test -e {} \; -print | xargs rm -f || true

# Remove dpkg and diffutils
echo "Removing dpkg ..."
echo "Deleting hooks ..."
rm -f /var/lib/dpkg/info/dpkg.p*
rm -f /etc/dpkg/dpkg.cfg.d/pkg-config-hook-config
echo "Removing dpkg package ..."
dpkg --purge --force-all dpkg || true

# Move tools to busybox
echo "Move tools to busybox ..."
busybox --install

echo "Creating mandatory symlinks ..."
# Links busybox as shell
rm -f /bin/sh
ln -f /usr/bin/busybox /bin/sh
ls -lah /bin/sh
# Link getty
rm -f /sbin/getty
ln -f /usr/bin/busybox /sbin/getty
ls -lah /sbin/getty
rm -f /bin/setsid
ln -f /usr/bin/busybox /bin/setsid
ls -lah /bin/setsid
