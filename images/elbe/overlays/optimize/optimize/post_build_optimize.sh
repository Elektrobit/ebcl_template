#!/bin/sh

ROOT_MNT=$1

# delete additional not required data
echo "Removing additional not needed data ..."
rm -f ${ROOT_MNT}/linuxrc
rm -rf ${ROOT_MNT}/var/log/*
rm -rf ${ROOT_MNT}/var/cache/*
rm -rf ${ROOT_MNT}/var/lib/systemd
rm -rf ${ROOT_MNT}/usr/share/man
rm -rf ${ROOT_MNT}/lost+found
rm -rf ${ROOT_MNT}/media
rm -rf ${ROOT_MNT}/mnt
rm -rf ${ROOT_MNT}/opt
rm -rf ${ROOT_MNT}/srv
rm -rf ${ROOT_MNT}/usr/lib/udev
rm -rf ${ROOT_MNT}/usr/lib/systemd

# delete optimize scripts
echo "Removing optimize scripts ..."
rm -rf ${ROOT_MNT}/optimize

# delete post-inst generated stuff for removed packages
echo "Removing left-overs of removed packages ..."
rm -f ${ROOT_MNT}/etc/adduser.conf
