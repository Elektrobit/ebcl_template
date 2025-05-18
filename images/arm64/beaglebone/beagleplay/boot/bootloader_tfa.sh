#!/bin/sh

. "${PWD}/../boot/bootloader_env.sh"

#export LD_LIBRARY_PATH=/workspace/sysroot_aarch64/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
#export PATH=/workspace/sysroot_aarch64/bin:$PATH
#export CROSS_COMPILE=aarch64-linux-gnu-
#export CC=${CROSS_COMPILE}gcc
##export AS=${CROSS_COMPILE}as
#export LD=${CROSS_COMPILE}ld
#export AR=${CROSS_COMPILE}ar
#export OBJCOPY=${CROSS_COMPILE}objcopy
#export OBJDUMP=${CROSS_COMPILE}objdump
#export STRIP=${CROSS_COMPILE}strip
TI_FIRMWARE="10.01.10"
TRUSTED_FIRMWARE="v2.12.0"

if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/bl31.bin ] ; then
    #if [ ! -d ${PROJECT_HOME}/${BOOTLOADER_DIR}/ti-linux-firmware/ ] ; then
    #    echo "${CYAN}git clone -b ${TI_FIRMWARE} https://github.com/beagleboard/ti-linux-firmware.git${NC}"
    #    git clone -b ${TI_FIRMWARE} https://github.com/beagleboard/ti-linux-firmware.git --depth=10 ${PROJECT_HOME}/${BOOTLOADER_DIR}/ti-linux-firmware/
    #fi
    if [ ! -d ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/ ] ; then
        echo "${CYAN}git clone -b ${TRUSTED_FIRMWARE} https://github.com/TrustedFirmware-A/trusted-firmware-a.git${NC}"
        git clone -b ${TRUSTED_FIRMWARE} https://github.com/TrustedFirmware-A/trusted-firmware-a.git --depth=10 ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/
    fi
    echo "${CYAN}make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/ -j${CORES} CROSS_COMPILE=$CC64 CFLAGS= LDFLAGS= ARCH=aarch64 PLAT=k3 SPD=opteed $TFA_EXTRA_ARGS TARGET_BOARD=${TFA_BOARD} all${NC}"
    make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/ -j${CORES} CROSS_COMPILE=$CC64 CFLAGS= LDFLAGS= ARCH=aarch64 PLAT=k3 SPD=opteed $TFA_EXTRA_ARGS TARGET_BOARD=${TFA_BOARD} all

    if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/build/k3/${TFA_BOARD}/release/bl31.bin ] ; then
        echo "${RED}Failure in ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/${NC}"
        ls -lha ${DIR}/trusted-firmware-a/
        exit 2
    else
        cp -v ${PROJECT_HOME}/${BOOTLOADER_DIR}/trusted-firmware-a/build/k3/${TFA_BOARD}/release/bl31.bin ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/
    fi
else
    echo "trusted firmware ${BLUE}${PROJECT_HOME}/${BOOTLOADER_DIR}/public/bl31.bin already present${NC}"
fi
