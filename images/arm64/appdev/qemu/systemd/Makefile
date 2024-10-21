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
kernel_cmdline_append = rw
# Expose SSH port on host
qemu_net_append = ,ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3,hostfwd=tcp::2222-:22,hostfwd=tcp::3333-:3333

# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_aarch64.mk

.PHONY: ssh
ssh:
	ssh-keygen -f "/home/ebcl/.ssh/known_hosts" -R "[localhost]:2222"
	ssh -p 2222 root@localhost
