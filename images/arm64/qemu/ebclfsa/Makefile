SHELL := /bin/bash

arch = aarch64

result_folder ?= ./build

demo_app ?= /workspace/apps/ebclfsa-demo

#### Low Integrity VM

result_folder_li ?= $(result_folder)/li

li_root_filesystem_spec ?= li/root.yaml
li_base_tarball ?= $(result_folder_li)/root.tar
li_config_root ?= li/config_root.sh
li_root_tarball ?= $(result_folder_li)/root.config.tar

li_boot_spec ?= li/boot.yaml
li_kernel ?= $(result_folder_li)/Image_li

li_initrd_spec ?= li/initrd.yaml
li_initrd_img ?= $(result_folder_li)/initrd.img

li_demo_builddir ?= $(result_folder_li)/demo
li_demo_install_dir ?= $(li_demo_builddir)/install
li_demo_install_dir_dummy ?= $(li_demo_install_dir)/remove_me
li_demo_install ?= $(li_demo_install_dir)/usr/bin/li_demo

#### High Integrity VM

result_folder_hi ?= $(result_folder)/hi

hi_root_filesystem_spec ?= hi/root.yaml
hi_base_tarball ?= $(result_folder_hi)/root.tar
hi_config_root ?= hi/config_root.sh
hi_root_tarball ?= $(result_folder_hi)/root.config.tar
hi_sysroot_tarball ?= $(result_folder_hi)/root_sysroot.tar

hi_boot_spec ?= hi/boot.yaml
hi_kernel ?= $(result_folder_hi)/Image_hi

hi_demo_builddir ?= $(result_folder_hi)/demo
hi_demo_install_dir ?= $(hi_demo_builddir)/install
hi_demo_install_dir_dummy ?= $(hi_demo_install_dir)/remove_me
hi_demo_install ?= $(hi_demo_install_dir)/hi_main $(hi_demo_install_dir)/hi_forward

### Tools / Hypervisor config

tools_extract_spec ?= tools_extract.yaml
tools_spec ?= tools.yaml
tools_root ?= $(result_folder)/tools.tar

template_extension_dir ?= $(result_folder)/noml
uboot ?= $(result_folder)/uboot-qemu-bart.elf
template_schema ?= $(template_extension_dir)/schema.yaml
hv_config ?= hv/hv-qemu.yaml
hv_config_deps ?= hv/hv-base.yaml
hv_config_dir ?= $(result_folder)/hv_config
hv_modules ?= $(hv_config_dir)/modules.list
hv_device_trees ?= $(wildcard hv/*.dts hv/*.dtsi)

hv_spec ?= hv.yaml
bootstrap ?= build/bootstrap.uimage

#### Image

image_spec ?= image.yaml
image ?= $(result_folder)/image.raw

default: all

$(li_demo_builddir)/Makefile:
	cmake -S $(demo_app) -B $(li_demo_builddir) --preset li-app

# Ensure that install is executed every time, otherwiese changes may be ignored
.PHONY: li_demo_install
li_demo_install: $(li_demo_builddir)/Makefile
	make -C $(li_demo_builddir) install DESTDIR=install

$(li_demo_install): li_demo_install

# Ensure that a file in the directory exists, so li_base_tarball does not fail
# because there are no files, although it does not use it. TODO: Remove when toolchain is fixed
$(li_demo_install_dir_dummy):
	mkdir -p $(li_demo_install_dir)
	touch $@

$(li_base_tarball): $(li_root_filesystem_spec) $(li_demo_install_dir_dummy) | li_demo_install
	@echo "Build $(hi_base_tarball)..."
	mkdir -p $(result_folder_li)
	set -o pipefail && root_generator --no-config $< $(result_folder_li) 2>&1 | tee $@.log

$(li_root_tarball): $(li_base_tarball) $(li_config_root) $(li_demo_install)
	@echo "Configuring ${li_root_tarball} as $@..."
	mkdir -p $(result_folder)
	set -o pipefail && root_configurator $(li_root_filesystem_spec) $(li_base_tarball) $@ 2>&1 | tee $@.log

$(li_kernel): $(li_boot_spec)
	@echo "Fetching li kernel..."
	mkdir -p $(result_folder_li)
	rm -f $(result_folder_li)/vmlinuz*
	set -o pipefail && boot_generator $< $(result_folder_li) 2>&1 | tee $@.log
# Extract the kernel, we need a raw Image
	zcat $(result_folder_li)/vmlinuz* > $(li_kernel)

$(li_initrd_img): $(li_initrd_spec)
	@echo "Build li initrd..."
	mkdir -p $(result_folder_li)
	set -o pipefail && initrd_generator $< $(result_folder_li) 2>&1 | tee $@.log


##### high integrity


$(hi_demo_builddir)/Makefile:
	cmake -S $(demo_app) -B $(hi_demo_builddir) --preset hi-app

# Ensure that install is executed every time, otherwiese changes may be ignored
.PHONY: li_demo_install
hi_demo_install: $(hi_demo_builddir)/Makefile
	make -C $(hi_demo_builddir) install DESTDIR=install

$(hi_demo_install): hi_demo_install

# Ensure that a file in the directory exists, so hi_base_tarball does not fail
# because there are no files, although it does not use it. TODO: Remove when toolchain is fixed
$(hi_demo_install_dir_dummy):
	mkdir -p $(hi_demo_install_dir)
	touch $@

$(hi_base_tarball): $(hi_root_filesystem_spec) $(hi_demo_install_dir_dummy) | hi_demo_install
	@echo "Build $(hi_base_tarball)..."
	mkdir -p $(result_folder_hi)
	set -o pipefail && root_generator --no-config $< $(result_folder_hi) 2>&1 | tee $@.log

$(hi_root_tarball): $(hi_base_tarball) $(hi_config_root) $(hi_demo_install)
	@echo "Configuring ${hi_root_tarball} as $@..."
	mkdir -p $(result_folder)
	set -o pipefail && root_configurator $(hi_root_filesystem_spec) $(hi_base_tarball) $@ 2>&1 | tee $@.log

$(hi_kernel): $(hi_boot_spec)
	@echo "Fetching hi kernel..."
	mkdir -p $(result_folder_hi)
	rm -f $(result_folder_hi)/vmlinux*
	set -o pipefail && boot_generator $< $(result_folder_hi) 2>&1 | tee $@.log
	mv $(result_folder_hi)/vmlinux* $(hi_kernel)

$(hi_sysroot_tarball): $(hi_root_filesystem_spec)
	@echo "Build hi sysroot.tar..."
	mkdir -p $(result_folder_hi)
	set -o pipefail && root_generator --sysroot --no-config $(hi_root_filesystem_spec) $(result_folder_hi) 2>&1 | tee $@.log


$(tools_root): $(tools_spec)
	@echo "Build $@ from $(tools_spec)..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --no-config $(tools_spec) $(result_folder) 2>&1 | tee $@.log

$(template_schema) $(uboot): $(tools_extract_spec) $(tools_root)
	@echo "Extracting required files from tools ..."
	rm -rf $(template_extension_dir)
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(tools_extract_spec) $(result_folder) 2>&1 | tee $(result_folder)/$(tools_extract_spec).log
# Ensure that the extracted files are newer than the source
	touch $@

$(hv_modules): $(template_schema) $(hv_config) $(hv_config_deps)
	hypervisor_config -s $(template_extension_dir) $(hv_config) $(hv_config_dir)

$(bootstrap): $(hv_spec) $(hv_modules) $(hi_kernel) $(li_kernel) $(li_initrd_img) $(hv_device_trees)
	@echo "Build ..."
	set -o pipefail && boot_generator $(hv_spec) $(result_folder) 2>&1 | tee $(result_folder)/$(hv_spec).log
# We do not need the config folder copied back....
	rm -rf $(result_folder)/config
# Ensure that the extracted file is newer than the source
	touch $@

$(image): $(bootstrap) $(li_root_tarball) $(hi_root_tarball) $(image_spec)
	embdgen $(image_spec) -o $@

all: $(image)

qemu: $(image) $(uboot)
	qemu-system-aarch64 \
		-M virt,virtualization=true,gic-version=3 \
		-cpu cortex-a57 \
		-m 4096 \
		-smp 8 \
		-serial stdio \
		-nographic \
		-monitor none \
		-kernel $(uboot) \
		-drive if=none,format=raw,file=$(image),id=vd0 \
		-device virtio-blk-device,drive=vd0 \
		-netdev user,id=net0,net=192.168.7.0/24,dhcpstart=192.168.7.2,dns=192.168.7.3,host=192.168.7.5,hostfwd=tcp::2222-:22,hostfwd=tcp::3333-:3333 \
		-device virtio-net-device,netdev=net0

# install the sysroot tarball
.PHONY: sysroot_install
hi_sysroot_install: $(hi_sysroot_tarball)
	rm -rf /workspace/sysroot_$(arch)/*
	tar -xf $(hi_sysroot_tarball) -C /workspace/sysroot_$(arch)/ >> /dev/null

# clean - delete the generated artifacts
.PHONY: clean
clean:
	rm -rf $(result_folder)
