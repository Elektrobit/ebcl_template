# Makefile for QEMU amd64 images

# QEMU images require three artefacts:
# - root filesystem image (image.raw)
# - Linux kernel binary (vmlinuz)
# - Initrd image (initrd.img)

# The initrd image is needed because the Canonical kernel has no
# built-in support for virtio block devices.

#--------------------
# Generated artefacts
#--------------------

# Disc image
ifeq ($(disc_image),)
disc_image = build/image.raw
endif

# Base root tarball
ifeq ($(base_tarball),)
base_tarball = build/ubuntu.tar
endif

# Configured root tarball
ifeq ($(root_tarball),)
root_tarball = build/ubuntu.config.tar
endif

# Generated initrd.img
ifeq ($(initrd_img),)
initrd_img = build/initrd.img
endif

# Kernel image
ifeq ($(kernel),)
kernel = build/vmlinuz
endif

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
boot: $(kernel)

# config the root tarball
.PHONY: config
config: $(root_tarball)

# clean - delete the generated artefacts
.PHONY: clean
clean:
	rm -rf build

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
	embdgen -o ./$(disc_image) $(partition_layout) 2>&1 | tee $(disc_image).log

$(base_tarball): $(root_filesystem_spec)
	@echo "Build root.tar..."
	mkdir -p build
	root_generator --no-config $(root_filesystem_spec) ./build 2>&1 | tee $(base_tarball).log

$(root_tarball): $(base_tarball) $(config_root)
	@echo "Configuring ${base_tarball} as ${root_tarball}..."
	mkdir -p build
	root_configurator $(root_filesystem_spec) $(base_tarball) $(root_tarball) 2>&1 | tee $(root_tarball).log

$(kernel): $(boot_spec)
	@echo "Get kernel binary..."
	mkdir -p build
	boot_generator $(boot_spec) ./build 2>&1 | tee $(kernel).log
	mv ./$(kernel)-* ./$(kernel) || true

$(initrd_img): $(initrd_spec)
	@echo "Build initrd.img..."
	mkdir -p build
	initrd_generator $(initrd_spec) ./build 2>&1 | tee $(initrd_img).log
