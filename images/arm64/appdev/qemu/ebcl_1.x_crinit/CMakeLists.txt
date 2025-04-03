cmake_minimum_required(VERSION 3.31)

project(qemu-appdev-ebcl_1.x_crinit-arm64)

include(/workspace/cmake/ebcl_sdk.cmake)

add_rootfs(root root.yaml)
add_initrd(initrd ../initrd.yaml)
add_kernel(kernel ../boot.yaml)

add_image(image
    ../../../../common/qemu/image.yaml.in
    ARTIFACT root ROOT_IMAGE
)

add_run_qemu(qemu
    ARCH aarch64
    INITRD initrd
    IMAGE image
    KERNEL kernel
    MEMORY 4G
    TCP_FORWARD :2222 :22
    TCP_FORWARD :3333 :3333
    NET_CONFIG ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3
    CMDLINE "console=ttyAMA0"
)
