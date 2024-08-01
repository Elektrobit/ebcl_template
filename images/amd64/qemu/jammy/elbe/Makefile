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

.PHONY: config
config: build/ubuntu.config.tar

.PHONY: qemu
qemu: build/vmlinuz build/initrd.img build/image.raw
	@echo "Running build/image.raw in QEMU..."
	qemu-system-x86_64 \
		-nographic -m 4G \
		-netdev user,id=mynet0 \
		-device virtio-net-pci,netdev=mynet0 \
		-kernel build/vmlinuz \
		-append "console=ttyS0" \
		-initrd build/initrd.img \
		-drive format=raw,file=build/image.raw,if=virtio

build/image.raw: build/ubuntu.config.tar image.yaml
	@echo "Build image..."
	mkdir -p build
	embdgen -o ./build/image.raw image.yaml

build/ubuntu.tar: root.yaml
	@echo "Build root.tar..."
	mkdir -p build
	root_generator --no-config root.yaml ./build

build/ubuntu.config.tar: build/ubuntu.tar config_root.sh
	@echo "Build root.tar..."
	mkdir -p build
	root_configurator root.yaml build/ubuntu.tar build/ubuntu.config.tar 

build/vmlinuz: ../boot.yaml
	@echo "Get kernel binary..."
	mkdir -p build
	boot_generator ../boot.yaml ./build
	mv ./build/vmlinuz-* ./build/vmlinuz

build/initrd.img: ../initrd.yaml
	@echo "Build initrd.img..."
	mkdir -p build
	initrd_generator ../initrd.yaml ./build

.PHONY: clean
clean:
	rm -rf build

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
