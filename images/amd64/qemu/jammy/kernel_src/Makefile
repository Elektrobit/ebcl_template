# Makefile for ammy QEMU amd64 image using a local build kernel

# Arch for sysroot extraction
arch = x86_64

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec = ../root.yaml
# Specification of the initrd.img
initrd_spec = initrd.yaml
# Specification of the kernel
boot_spec = boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = ../config_root.sh

#-------------------
# Run the QEMU image
#-------------------

# QEMU kernel commandline
kernel_cmdline_append = rw

#--------------------
# Generated artifacts
#--------------------

# Disc image
disc_image = $(result_folder)/image.raw

# Base root tarball
base_tarball = $(result_folder)/ubuntu.tar

# Configured root tarball
root_tarball = $(result_folder)/ubuntu.config.tar

# Generated initrd.img
initrd_img = $(result_folder)/initrd.img

# Kernel image
kernel = $(result_folder)/vmlinuz

# Sysroot tarball
sysroot_tarball = $(result_folder)/ubuntu_sysroot.tar

# Kernel modules
modules = $(result_folder)/lib

# Kernel config
kconfig = $(result_folder)/config

# Kernel source
source = kernel

# Path of the kernel sources
kernel_dir = $(source)/linux-5.15.0

#-----------------------
# Include base makefiles
#-----------------------

# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_x86_64.mk

#--------------------------
# Image build configuration
#--------------------------

$(kernel): $(kconfig) $(source)
	@echo "Get kernel binary..."
	cd $(kernel_dir) && yes "" | $(MAKE) -j 16 bzImage
	cd $(kernel_dir) && INSTALL_PATH=../../$(result_folder) $(MAKE) install
	cp -v $(result_folder)/vmlinuz-* $(kernel)
	@echo "Results were written to $(kernel)"

$(modules): $(kernel)
	@echo "Get virtio driver..."
	cd $(kernel_dir) && $(MAKE) -j 16 modules
	cd $(kernel_dir) && chmod +x debian/scripts/sign-module
	mkdir -p $(result_folder)
	cd $(kernel_dir) && INSTALL_MOD_PATH=../../$(result_folder) $(MAKE) modules_install

$(source):
	@echo "Get kernel sources..."
	mkdir -p kernel
	cd kernel && apt -y source linux
	sudo apt -y build-dep linux
	cd $(kernel_dir) && chmod +x scripts/*.sh

$(kconfig): $(boot_spec) $(source)
	@echo "Get kernel config as $(kconfig)..."
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(boot_spec) $(result_folder) 2>&1 | tee $(kconfig).log
	@echo "Renaming $(result_folder)/config-* as $(kconfig)..."
	mv $(result_folder)/config-* $(kconfig)
	@echo "Copying $(kconfig) to $(kernel_dir)..."
	cp $(kconfig) $(kernel_dir)/.config
	@echo "Set all not defined values of the kernel config to defaults..."
	cd $(kernel_dir) && yes "" | $(MAKE) $(kernel_make_args) olddefconfig
	@echo "Copying modified config as olddefconfig..."
	cp $(kernel_dir)/.config $(result_folder)/olddefconfig

$(initrd_img): $(initrd_spec) $(modules)
	@echo "Build initrd.img..."
	mkdir -p $(result_folder)
	set -o pipefail && initrd_generator $(initrd_spec) $(result_folder) 2>&1 | tee $(initrd_img).log


#--------------------
# Helper make targets
#--------------------

# Rebuild the kernel binary
.PHONY: rebuild_kernel
rebuild_kernel:
	mkdir -p $(result_folder)
	cd $(kernel_dir) && yes "" | $(MAKE) -j 16 bzImage
	cd $(kernel_dir) && INSTALL_PATH=../../$(result_folder) $(MAKE) install
	cp -v $(result_folder)/vmlinuz-* $(kernel)
	@echo "Results were written to $(kernel)"

# Rebuild the kernel modules
.PHONY: rebuild_modules 
rebuild_modules: kernel
	mkdir -p $(result_folder)
	cd $(kernel_dir) && $(MAKE) modules -j 16
	cd $(kernel_dir) && chmod +x debian/scripts/sign-module
	rm -rf build/lib
	cd $(kernel_dir) && INSTALL_MOD_PATH=../../$(result_folder) $(MAKE) modules_install

# clean - delete the generated artifacts
.PHONY: clean
clean:
	rm -rf $(result_folder)

.PHONY: clean_kernel
clean_kernel:
	rm -rf $(source)
