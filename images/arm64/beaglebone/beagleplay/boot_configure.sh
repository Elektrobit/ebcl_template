#!/bin/sh

# The outdir is created and populated in such a way so it adheres to the boot partition filesystem layout
# boot_extract will extract toplevel files directly and files that need to be in specific subfolders from /outdir
# e.g expected layout:
#       extlinux
#          |------ extlinux.conf

ls -lah
ls -lah boot/
ls -lah boot/dtbs/

export KERNEL_VERSION=$(ls boot/dtbs/ | sort | tail -n 1)

echo "Using kernel version: ${KERNEL_VERSION}"

mkdir -p outdir/extlinux
mkdir -p outdir/ti

cp opt/u-boot/bb-u-boot-beagleplay/microsd-extlinux.conf outdir/extlinux/extlinux.conf
sed -i 's:init=[^ ]*:init=/usr/bin/init:g' outdir/extlinux/extlinux.conf

cp boot/dtbs/${KERNEL_VERSION}/*/k3-am625-*.dtb outdir/
cp boot/dtbs/${KERNEL_VERSION}/*/k3-am625-*.dtb outdir/ti

cp boot/vmlinuz-${KERNEL_VERSION} outdir/
mv outdir/vmlinuz* outdir/Image.gz
gzip -d outdir/Image.gz

mkdir -p outdir/overlays

cp -r boot/dtbs/${KERNEL_VERSION}/*/overlays outdir/
cp -r boot/dtbs/${KERNEL_VERSION}/*/*.dtbo outdir/overlays
