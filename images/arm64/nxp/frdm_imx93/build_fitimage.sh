#!/bin/sh
. "/workspace/images/arm64/nxp/frdm_imx93/bootloader/frdm_imx93_env.sh"
# Paths (adjust to your layout)
echo "Creating the boot.scr"
mkimage -A arm64 -T script -C none -n "EB FIT boot script" -d build/boot.cmd build/boot.scr
echo "Creating the fit.itb"
mkimage -f build/frdm_imx93_fit.its -k ../keys -r build/fit.itb

