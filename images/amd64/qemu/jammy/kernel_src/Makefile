.PHONY: default
default: qemu

.PHONY: image
image: build/image.raw

.PHONY: initrd
initrd: build/initrd.img

.PHONY: qemu
qemu: build/vmlinux build/initrd.img build/image.raw
	@echo "Running build/image.raw in QEMU..."
	qemu-system-x86_64 \
		-nographic -m 4G \
		-netdev user,id=mynet0 \
		-device virtio-net-pci,netdev=mynet0 \
		-kernel build/vmlinux \
		-append "console=ttyS0" \
		-initrd build/initrd.img \
		-drive format=raw,file=build/image.raw,if=virtio

build/image.raw: build/ubuntu.tar image.yaml
	@echo "Build image..."
	mkdir -p build
	embdgen -o ./build/image.raw image.yaml

build/ubuntu.tar: root.yaml
	@echo "Build root.tar..."
	mkdir -p build
	root_generator root.yaml ./build

build/vmlinux: build/config kernel
	@echo "Get kernel binary..."
	ls -lah
	cp build/config kernel/linux-5.15.0/.config
	cd kernel/linux-5.15.0 && $(MAKE) -j 16
	cp kernel/linux-5.15.0/vmlinux build/vmlinux

build/lib: build/vmlinux
	@echo "Get virtio driver..."
	cd kernel/linux-5.15.0 && $(MAKE) modules -j 16
	cd kernel/linux-5.15.0 && chmod +x debian/scripts/sign-module
	mkdir -p build
	cd kernel/linux-5.15.0 && INSTALL_MOD_PATH=../../build $(MAKE) modules_install

kernel:
	@echo "Get kernel sources..."
	mkdir -p kernel
	cd kernel && apt -y source linux
	sudo apt -y build-dep linux
	cd kernel/linux-5.15.0 && chmod +x scripts/*.sh

build/config: ../boot.yaml
	@echo "Get kernel config..."
	mkdir -p build
	boot_generator ../boot.yaml ./build
	mv ./build/config-* ./build/config

build/initrd.img: initrd.yaml build/lib
	@echo "Build initrd.img..."
	mkdir -p build
	initrd_generator initrd.yaml ./build

.PHONY: clean
clean:
	rm -rf build
	rm -rf kernel
