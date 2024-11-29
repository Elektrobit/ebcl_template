SHELL := /bin/bash

arch = x86_64

result_folder ?= ./build


#### Xem Dom U

result_folder_domu ?= $(result_folder)/domu

domu_root_filesystem_spec ?= domu/crinit/root.yaml
domu_boot_filesystem_spec ?= domu/boot.yaml
domu_base_tarball ?= $(result_folder_domu)/ebcl.tar
domu_config_root ?= domu/crinit/config_root.sh
domu_root_tarball ?= $(result_folder_domu)/ebcl.config.tar
domu_boot_tarball_spec ?= domu/boot_root.yaml
domu_boot_tarball ?= $(result_folder_domu)/boot_root.tar
domu_boot_spec ?= domu/boot.yaml
domu_boot ?= $(result_folder_domu)/boot.tar
domu_image_spec ?= domu_image.yaml
domu_image ?= dom0/systemd/domu/opt/images/domu.img

#### Xen Dom0

result_folder_dom0 ?= $(result_folder)/dom0

dom0_root_filesystem_spec ?= dom0/systemd/root.yaml
dom0_base_tarball ?= $(result_folder_dom0)/ebcl.tar
dom0_config_root ?= dom0/systemd/config_root.sh
dom0_config_grub ?= dom0/systemd/config_grub.sh
dom0_root_tarball ?= $(result_folder_dom0)/ebcl.config.tar

#### Dom0 containing DomU image

image_spec ?= dom0_image.yaml
image ?= $(result_folder)/image.raw

default: all

##### DomU

$(domu_base_tarball): $(domu_root_filesystem_spec)
	@echo "Build $(domu_base_tarball)..."
	mkdir -p $(result_folder_domu)
	set -o pipefail && root_generator --no-config $< $(result_folder_domu) 2>&1 | tee $@.log

$(domu_root_tarball): $(domu_base_tarball) $(domu_config_root)
	@echo "Configuring ${domu_root_tarball} as $@..."
	mkdir -p $(result_folder)
	set -o pipefail && root_configurator $(domu_root_filesystem_spec) $(domu_base_tarball) $@ 2>&1 | tee $@.log

$(domu_boot_tarball): $(domu_boot_tarball_spec)
	@echo "Build $(domu_boot_tarball) ..."
	mkdir -p $(result_folder_domu)
	set -o pipefail && root_generator --no-config $(domu_boot_tarball_spec) $(result_folder_domu) 2>&1 | tee $@.log

$(domu_boot): $(domu_boot_tarball)
	@echo "Build $(domu_boot)..."
	mkdir -p $(result_folder_domu)
	set -o pipefail && boot_generator $(domu_boot_spec) $(result_folder_domu) 2>&1 | tee $@.log

#### DomU image

$(domu_image): $(domu_root_tarball) $(domu_boot) $(domu_image_spec)
	echo "Building DomU image..."
	embdgen $(domu_image_spec) -o $@ 2>&1 | tee $@.log

##### Dom0

$(dom0_base_tarball): $(dom0_root_filesystem_spec)
	@echo "Build $(domu_base_tarball)..."
	mkdir -p $(result_folder_dom0)
	set -o pipefail && root_generator --no-config $< $(result_folder_dom0) 2>&1 | tee $@.log

$(dom0_root_tarball): $(dom0_base_tarball) $(dom0_config_root) $(domu_image)
	@echo "Configuring ${dom0_root_tarball} as $@..."
	mkdir -p $(result_folder)
	set -o pipefail && root_configurator $(dom0_root_filesystem_spec) $(dom0_base_tarball) $@ 2>&1 | tee $@.log

#### Dom0 image

$(image): $(dom0_root_tarball) $(image_spec)
	echo "Building Dom0 image..."
	embdgen $(image_spec) -o $@ 2>&1 | tee $@.log
	echo "Configure grub on efi partition..."
	set -o pipefail && ./$(dom0_config_grub) $@ 2>&1 | tee -a $@.log

all: $(image)

qemu_net_append ?=

qemu: $(image)
	qemu-system-x86_64 \
        -m 4096 \
		-nographic \
		-netdev user,id=mynet0$(qemu_net_append) \
		-device virtio-net-pci,netdev=mynet0 \
		-drive format=raw,file=$(image),if=virtio \
		-bios /usr/share/ovmf/OVMF.fd

# clean - delete the generated artifacts
.PHONY: clean
clean:
	rm -rf $(result_folder)
	rm -rf $(domu_image)
	rm -rf $(domu_image).log
