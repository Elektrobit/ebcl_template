#!/bin/sh
echo "Creating the boot.scr"
mkimage -A arm64 -T script -C none -n "EB FIT boot script" -d build/boot.cmd build/boot.scr
echo "Creating the fit.itb"
mkimage -f build/frdm_imx93_fit.its build/fit.itb

