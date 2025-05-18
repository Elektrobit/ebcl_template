#!/bin/sh

. "${PWD}/../boot/bootloader_env.sh"
UBOOT="v2025.01-Beagle"

if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tiboot3.bin ] ; then
    if [ ! -d ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot ] ; then
        global="https://github.com/beagleboard/u-boot.git"
        mirror="${global}"

        echo "${CYAN}git clone -b ${UBOOT} ${mirror} --depth=10 ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot/${NC}"
        git clone -b ${UBOOT} ${mirror} --depth=10 ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot/
    fi

    echo "${CYAN}make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR CROSS_COMPILE=$CC32 $UBOOT_CFG_CORTEXR${NC}"
    make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR CROSS_COMPILE=$CC32 $UBOOT_CFG_CORTEXR

    echo "${CYAN}make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR CROSS_COMPILE=$CC32 BINMAN_INDIRS=${PROJECT_HOME}/${BOOTLOADER_DIR}/ti-linux-firmware/${NC}"
    make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR CROSS_COMPILE=$CC32 BINMAN_INDIRS=${PROJECT_HOME}/${BOOTLOADER_DIR}/ti-linux-firmware/

    if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR/tiboot3-${SOC_NAME}-${SECURITY_TYPE}-evm.bin ] ; then
        echo "${RED}Failure in u-boot CORTEXR build of [$UBOOT_CFG_CORTEXR]${NC}"
        ls -lha ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR/
        exit 2
    else
        cp -v ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR/tiboot3-${SOC_NAME}-${SECURITY_TYPE}-evm.bin ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tiboot3.bin
        if [ -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR/sysfw-${SOC_NAME}-${SECURITY_TYPE}-evm.itb ] ; then
            cp -v ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR/sysfw-${SOC_NAME}-${SECURITY_TYPE}-evm.itb ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/sysfw.itb
        fi
    fi
else
    echo "${BLUE}CORTEXR u-boot binary ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tiboot3.bin already present${NC}"
fi

#rm -rf ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXR/ || true

