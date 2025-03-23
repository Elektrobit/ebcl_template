#! /bin/bash

lsblk -f
growpart /dev/mmcblk1 2 #sd card is mmcblk1 (mmcblk0 is the eMCC)
resize2fs /dev/mmcblk1p2 #2nd partiton of the sdcard which is the filesystem
df -h
