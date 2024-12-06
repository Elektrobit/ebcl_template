# Makefile for Jammy QEMU amd64 image using debootstrap

# Arch for sysroot extraction
arch = aarch64

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec = root.yaml
# Specification of the initrd.img
initrd_spec = ../initrd.yaml
# Specification of the kernel
boot_spec = ../boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = config_root.sh

#--------------------
# Generated artifacts
#--------------------

# Base root tarball
base_tarball = build/ebcl.tar

# Configured root tarball
root_tarball = build/ebcl.config.tar

# Sysroot tarball
sysroot_tarball = build/ebcl_sysroot.tar

#-------------------
# Run the QEMU image
#-------------------

# QEMU kernel commandline
kernel_cmdline_append = "rw"

# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_aarch64.mk
