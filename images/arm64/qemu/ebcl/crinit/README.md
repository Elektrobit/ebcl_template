# EB corbos Linux QEMU arm64 minimal example image

This is a minimal example image showing how to build small and fast solutions using EB corbos Linux.

The description of this this image is part of the EB corbos Linux SDK template, see _images/arm64/qemu/ebcl/crinit_ of https://github.com/Elektrobit/ebcl_template.

## Run the image

You can run the image on your machine if you have QEMU for aarch64 available.
On Ubuntu hosts, you can install QEMU with the command _sudo apt install qemu-system-arm_.

You can run the image using the command:

```bash
qemu-system-aarch64 \
    -machine virt -cpu cortex-a72 -machine type=virt -nographic -m 4G \
    -netdev user,id=mynet0,ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3 \
    -device virtio-net-pci,netdev=mynet0 \
    -kernel vmlinuz \
    -append "console=ttyAMA0 rw" \
    -initrd initrd.img \
    -drive format=raw,file=image.raw,if=virtio
```
or by running _run.sh_.
