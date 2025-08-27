#!/bin/sh
mkimage -A arm64 -T script -C none -n "EB FIT boot script" -d build/boot.cmd build/boot.scr
mkimage -f build/frdm_imx93_fit.its build/fit.itb

