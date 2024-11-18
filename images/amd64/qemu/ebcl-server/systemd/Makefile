# Makefile for Jammy QEMU amd64 image using debootstrap

# Arch for sysroot extraction
arch = x86_64

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
kernel_cmdline_append = 
# Expose SSH port on host
qemu_net_append = ,hostfwd=tcp::2223-:22

# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_x86_64.mk

.PHONY: ssh
ssh:
	ssh-keygen -f "/home/ebcl/.ssh/known_hosts" -R "[localhost]:2223"
	ssh -p 2223 root@localhost
