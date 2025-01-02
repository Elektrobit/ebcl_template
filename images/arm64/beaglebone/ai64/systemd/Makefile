# Makefile for Beaglebone AI64 systemd variant

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the initrd.img
initrd_spec = ../initrd.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec ?= root.yaml

config_root ?= config_root.sh

boot_extract_spec ?= ../boot_extract.yaml

boot_root_spec ?= ../boot_root.yaml

variant=systemd
#-------------------------
# Additional configuration
#-------------------------

include ../beaglebone.mk
