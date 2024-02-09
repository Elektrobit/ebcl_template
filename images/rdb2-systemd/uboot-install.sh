#!/bin/dash

set -eux

diskname=$1

# Dump ATF/u-boot image...
#
# 0x000000 - 0x0001B7 Bootloader (440 bytes) First part of uboot
# 0x0001B8 - 0x0001FF Signature and Partition table
# 0x000200 - 0x100000 Free space for second part of uboot
# 0x100000 - xxxxxxxx Boot partition
#
dd if=boot/fip.s32 of="${diskname}" conv=notrunc bs=256 count=1 seek=0
dd if=boot/fip.s32 of="${diskname}" conv=notrunc bs=512 seek=1 skip=1
