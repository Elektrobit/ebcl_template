.PHONY: default
default: qemu

.PHONY: image
image: build/image.raw

.PHONY: root
root: build/ubuntu.tar

.PHONY: initrd
initrd: build/initrd.img

.PHONY: boot
boot: build/boot.tar

.PHONY: efi
boot: build/efi.tar

.PHONY: qemu
qemu: build/image.raw
	@echo "Running build/image.raw in QEMU..."
	qemu-system-x86_64 \
		-m 4096 \
        -nographic \
        -netdev user,id=mynet0 \
        -device virtio-net-pci,netdev=mynet0 \
        -drive file=build/image.raw,if=virtio

build/image.raw: build/efi.tar build/boot.tar build/ubuntu.tar image.yaml
	@echo "Build image..."
	mkdir -p build
	embdgen -o ./build/image.raw image.yaml

build/ubuntu.tar: root.yaml jammy.xml
	@echo "Build root.tar..."
	mkdir -p build
	root_generator root.yaml ./build

build/boot.tar: boot.yaml grub.cfg build/initrd.img
	@echo "Generate boot archive..."
	mkdir -p build
	boot_generator boot.yaml ./build

build/efi.tar: efi.yaml
	@echo "Generate efi archive..."
	mkdir -p build
	boot_generator efi.yaml ./build

build/initrd.img: ../initrd.yaml
	@echo "Build initrd.img..."
	mkdir -p build
	initrd_generator ../initrd.yaml ./build

.PHONY: clean
clean:
	rm -rf build
