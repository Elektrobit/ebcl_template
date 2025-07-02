#!/bin/sh

. "${PWD}/../bootloader/bootloader_env.sh"

if [ ! -d ${PROJECT_HOME}/${KERNEL_DIR}/linux_build ] ; then
    if [ ! -d ${PROJECT_HOME}/${TOOLCHAIN_DIR}/ ] ; then
        ./../gcc/gcc.sh
    else
        echo "${ORANGE}${TOOLCHAIN_DIR} folder exist no toolchain will be extracted${NC}"
    fi

    export ARCH=arm64
    export CROSS_COMPILE=${PROJECT_HOME}/${TOOLCHAIN_DIR}/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-
    count=$(find ${TOOLCHAIN_DIR} 2>/dev/null | wc -l)
    if [ "$count" == 0 ]; then
        source gcc.sh || { exit 1 ; }
    else
        echo -e "${ORANGE}${TOOLCHAIN_DIR} folder exist no toolchain will be extracted${NC}"
    fi
    mkdir -p ${PROJECT_HOME}/${KERNEL_DIR}
    echo ${PROJECT_HOME}/${KERNEL_DIR}
    #cd ${PROJECT_HOME}/${BOOTLOADER_DIR}

    echo -e "${BLUE}"
    ${CC32}gcc --version
    ${CC64}gcc --version
    echo -e "${NC}"
    if [ ! -f ${PROJECT_HOME}/${DOWNLOAD_DIR}/v6.1.46-ti-arm64-r13.tar.gz ] ; then
    wget -P ${PROJECT_HOME}/${DOWNLOAD_DIR} https://github.com/beagleboard/linux/archive/refs/heads/v6.1.46-ti-arm64-r13.tar.gz
    fi
    if [ ! -d ${PROJECT_HOME}/${KERNEL_DIR}/linux-6.1.46-ti-arm64-r13 ] ; then
    tar -xf ${PROJECT_HOME}/${DOWNLOAD_DIR}/v6.1.46-ti-arm64-r13.tar.gz -C ${PROJECT_HOME}/${KERNEL_DIR}
    fi
    #make -C ${PROJECT_HOME}/${KERNEL_DIR}/linux-6.1.46-ti-arm64-r13 O=${PROJECT_HOME}/${KERNEL_DIR}/linux_build mrproper
    make -C ${PROJECT_HOME}/${KERNEL_DIR}/linux-6.1.46-ti-arm64-r13 O=${PROJECT_HOME}/${KERNEL_DIR}/linux_build defconfig
    make -C ${PROJECT_HOME}/${KERNEL_DIR}/linux-6.1.46-ti-arm64-r13 O=${PROJECT_HOME}/${KERNEL_DIR}/linux_build -j$(nproc)
    make -C ${PROJECT_HOME}/${KERNEL_DIR}/linux-6.1.46-ti-arm64-r13 O=${PROJECT_HOME}/${KERNEL_DIR}/linux_build modules_install INSTALL_MOD_PATH=${PROJECT_HOME}/${KERNEL_DIR}/linux_build -j$(nproc)
else
    echo "${ORANGE}${PROJECT_HOME}/${KERNEL_DIR}/linux_build folder exist which means kernel was already built. If the build was corrupted please delete the folder to force rebuild!${NC}"
fi
