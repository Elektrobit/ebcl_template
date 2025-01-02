#!/bin/sh

mkdir -p outdir/extlinux

cp opt/u-boot/bb-u-boot-beagleboneai64/microsd-extlinux.conf outdir/extlinux/extlinux.conf
sed -i 's:init=[^ ]*:init=/usr/bin/init:g' outdir/extlinux/extlinux.conf
cp boot/dtbs/*/*/k3-j721e-sk.dtb outdir/
cp boot/dtbs/*/*/k3-j721e-beagleboneai64.dtb outdir/
cp boot/vmlinuz* outdir/Image.gz
gzip -d outdir/Image.gz

cp -r boot/dtbs/*/*/overlays outdir/overlays

cp -r boot/dtbs/*/*/*.dtbo outdir/overlays