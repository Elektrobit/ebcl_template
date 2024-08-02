# Makefile for EB corbos Linux Ubunut Jammy AMD64 QEMU image

# QEMU images require three artefacts:
# - root filesystem image (image.raw)
# - Linux kernel binary (vmlinuz)
# - Initrd image (initrd.img)

# The initrd image is needed because the Canonical kernel has no
# built-in support for virtio block devices.

#---------------------
# Image specifications
#---------------------

# Specificaiton of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specificaiton of the root filesystem content and configuration
root_filesystem_spec = ../root.yaml
# Specificaiton of the initrd.img
initrd_spec = ../initrd.yaml
# Specificaiton of the kernel
boot_spec = ../boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = ../config_root.sh

#--------------------
# Generated artefacts
#--------------------

# Disc image
disc_image = build/image.raw
# Base root tarball
base_tarball = build/ubuntu.tar
# Configured root tarball
root_tarball = build/ubuntu.config.tar
# Generated initrd.img
initrd_img = build/initrd.img
# Kernel image
kernel = build/vmlinuz

#--------------------------------
# Default make targets for images
#--------------------------------

# default action
.PHONY: default
default: qemu

# build of the disc image
.PHONY: image
image: $(disc_image)

# build of the root tarball(s)
.PHONY: root
root: $(base_tarball)

# build of the initrd.img(s)
.PHONY: initrd
initrd: $(initrd_img)

# build of the kernel(s)
.PHONY: boot
boot: build/boot.tar

# config the root tarball
.PHONY: config
config: $(root_tarball)

# clean - delete the generated artefacts
.PHONY: clean
clean:
	rm -rf build

#-------------------
# Run the QEMU image
#-------------------
.PHONY: qemu
qemu: $(kernel) $(initrd_img) $(disc_image)
	@echo "Running $(disc_image) in QEMU..."
	qemu-system-x86_64 \
		-nographic -m 4G \
		-netdev user,id=mynet0 \
		-device virtio-net-pci,netdev=mynet0 \
		-kernel $(kernel) \
		-append "console=ttyS0" \
		-initrd $(initrd_img) \
		-drive format=raw,file=$(disc_image),if=virtio

#-------------------------------------------
# Open a shell for manual root configuration
#-------------------------------------------
.PHONY: edit_root
edit_root:
	@echo "Extacting root tarball..."
	mkdir -p build/root
	cd build && fakeroot -s fakedit -- tar xf ubuntu.config.tar -C ./root
	@echo "Open edit shell..."
	cd build/root && fakeroot -i ../fakedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	cd build && rm -f ubuntu.config.old.tar
	cd build && mv ubuntu.config.tar ubuntu.config.old.tar
	cd build/root && fakeroot -i ../fakedit -s ../fakedit -- tar cf ../ubuntu.config.tar .

#--------------------------
# Image build configuration
#--------------------------

$(disc_image): $(root_tarball) $(partition_layout)
	@echo "Build image..."
	mkdir -p build
	embdgen -o ./$(disc_image) $(partition_layout)

$(base_tarball): $(root_filesystem_spec)
	@echo "Build root.tar..."
	mkdir -p build
	root_generator --no-config $(root_filesystem_spec) ./build

$(root_tarball): $(base_tarball) $(config_root)
	@echo "Build root.tar..."
	mkdir -p build
	root_configurator $(root_filesystem_spec) $(base_tarball) $(root_tarball) 

$(kernel): $(boot_spec)
	@echo "Get kernel binary..."
	mkdir -p build
	boot_generator $(boot_spec) ./build
	mv ./$(kernel)-* ./$(kernel)

$(initrd_img): $(initrd_spec)
	@echo "Build initrd.img..."
	mkdir -p build
	initrd_generator $(initrd_spec) ./build
