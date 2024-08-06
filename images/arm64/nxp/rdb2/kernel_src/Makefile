# Makefile for NXP RDB2 with kernel build form source

#---------------------
# Image specifications
#---------------------

# Specificaiton of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specificaiton of the initrd.img
initrd_spec = ../initrd.yaml
# Specificaiton of the fitimage
boot_spec = ../boot.yaml
# Specificaiton of the root environment for fitimage building
boot_root_spec = ../boot_root.yaml
# Specificaiton of the root filesystem content and configuration
root_filesystem_spec = root.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = config_root.sh

# Build script for the fitimage
build_fitimage = ../build_fitimage.sh
# Layout of the fitimage
fitimage_config = ../bootargs.its
# NXP bootloader config
bootloader_config = ../bootargs-overlay.dts

include ../rdb2.mk

#--------------------
# Generated artefacts
#--------------------

# Kernel image
kernel = build/vmlinux
# Kernel modules
modules = build/lib
# Kernel config
kconfig = build/config
# Kernel source
source = kernel

#--------------------
# Helper make targets
#--------------------

# Rebuild the kernel binary
.PHONY: rebuild_kernel
rebuild_kernel:
	mkdir -p build
	cd kernel/linux-5.15.0 && $(MAKE) -j 16
	rm -f build/vmlinux
	cp kernel/linux-5.15.0/vmlinux build/vmlinux

# Rebuild the kernel modules
.PHONY: rebuild_modules 
rebuild_modules: kernel
	mkdir -p build
	cd kernel/linux-5.15.0 && $(MAKE) modules -j 16
	cd kernel/linux-5.15.0 && chmod +x debian/scripts/sign-module
	rm -rf build/lib
	cd kernel/linux-5.15.0 && INSTALL_MOD_PATH=../../build $(MAKE) modules_install

# clean - delete the generated artefacts
.PHONY: clean
clean:
	rm -rf kernel
	rm -rf build


#--------------------------
# Image build configuration
#--------------------------

$(kernel): $(kconfig) $(source)
	@echo "Get kernel binary..."
	cp build/config kernel/linux-5.15.0/.config
	cd kernel/linux-5.15.0 && $(MAKE) -j 16
	cp kernel/linux-5.15.0/vmlinux build/vmlinux

$(modules): $(kernel)
	@echo "Get virtio driver..."
	cd kernel/linux-5.15.0 && $(MAKE) modules -j 16
	cd kernel/linux-5.15.0 && chmod +x debian/scripts/sign-module
	mkdir -p build
	cd kernel/linux-5.15.0 && INSTALL_MOD_PATH=../../build $(MAKE) modules_install

$(source):
	@echo "Get kernel sources..."
	mkdir -p kernel
	cd kernel && apt -y source linux
	sudo apt -y build-dep linux
	cd kernel/linux-5.15.0 && chmod +x scripts/*.sh

$(kconfig): $(boot_spec)
	@echo "Get kernel config..."
	mkdir -p build
	set -o pipefail && boot_generator ../boot.yaml ./build 2>&1 | tee build/$(kconfig).log
	mv ./build/config-* ./build/config

$(initrd_img): $(initrd_spec) $(modules)
	@echo "Build initrd.img..."
	mkdir -p build
	set -o pipefail && initrd_generator $(initrd_spec) ./build 2>&1 | tee build/$(initrd_img).log
