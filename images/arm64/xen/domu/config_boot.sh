#!/bin/sh

set -e

# pvgrub has hard time with zstd compressed kernel and trying to use such produces "error: not xen image".
# Uncompress the kernel with "extract-vmlinux", available in kernel source package.

KERNEL=$(ls /boot/vmlinuz-*)
KERNEL_VERSION=$(echo ${KERNEL} | cut -d "-" -f 2)
KERNEL_SOURCE_DIR="/usr/src/linux-source-${KERNEL_VERSION}"
KERNEL_SOURCE_TAR="linux-source-${KERNEL_VERSION}.tar.bz2"
UNCOMPRESSED="/boot/vmlinux"

echo "Extracting extract-vmlinux..."
tar xf ${KERNEL_SOURCE_DIR}/${KERNEL_SOURCE_TAR} --strip-components=2 linux-source-${KERNEL_VERSION}/scripts/extract-vmlinux

echo "Extracting ${KERNEL} to ${UNCOMPRESSED}..."
./extract-vmlinux ${KERNEL} > ${UNCOMPRESSED}

echo "Done!"
