cmake_minimum_required(VERSION 3.31)

project(qemu-ebclfsa)

include(/workspace/cmake/ebcl_sdk.cmake)
include(cmake/internal.cmake)

add_rootfs(tools tools_cmake.yaml)

# Low integrity vm
add_cmake_build(demo_li /workspace/apps/ebclfsa-demo li-app)
add_rootfs(li_root 
    li/root.yaml.in
    OUTPUT_DIR demo_li DEMO_DIR
)
add_initrd(li_initrd
    li/initrd.yaml
)
add_kernel(li_kernel
    li/boot.yaml
    UNPACK
)

# High integrity vm
add_cmake_build(demo_hi /workspace/apps/ebclfsa-demo hi-app)
add_rootfs(hi_root 
    hi/root.yaml.in
    OUTPUT_DIR demo_hi DEMO_DIR
)
add_kernel(hi_kernel
    hi/boot.yaml
    UNPACK
)

# Hypervisor
add_hypervisor_config(hv_config
    hv/hv-qemu.yaml
    SPECIALIZATION base.yaml eb-hv-qemu-noml-config-extension
)

add_hypervisor(
    hv
    hv.yaml.in
    OUTPUT_DIR hv_config HV_CONFIG_DIR
    ARTIFACT li_kernel LI_KERNEL
    ARTIFACT hi_kernel HI_KERNEL
    ARTIFACT li_initrd LI_INITRD
    ARTIFACT tools TOOLS_TAR
)

# Image
add_uboot(uboot 
    tools_extract.yaml.in
    ARTIFACT tools TOOLS
)
add_image(image
    image.yaml.in
    ARTIFACT hv HV
    ARTIFACT li_root LI
    ARTIFACT hi_root HI
)

# Run qemu
add_run_qemu(qemu
    KERNEL uboot
    IMAGE  image
    CPUS   8
    MEMORY 4096
    TCP_FORWARD :10022 :22
    TCP_FORWARD :1234  :1234
    TCP_FORWARD :5000  192.168.7.100:5000
    NET_CONFIG  net=192.168.7.0/24,dhcpstart=192.168.7.2,dns=192.168.7.3,host=192.168.7.5
)
