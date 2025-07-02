#!/bin/sh

. "${PWD}/../bootloader/bootloader_env.sh"

#export LD_LIBRARY_PATH=/workspace/sysroot_aarch64/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
#export CROSS_COMPILE=/workspace/sysroot_aarch64/bin/aarch64-linux-gnu-

#export AS=aarch64-linux-gnu-as
#export PYTHON3=/build/venv/bin/python3
#export PATH=/build/venv/bin:$PATH
#export CROSS_COMPILE=aarch64-linux-gnu-
#export CC=${CROSS_COMPILE}gcc
#export AS=${CROSS_COMPILE}as
#export LD=${CROSS_COMPILE}ld
#export AR=${CROSS_COMPILE}ar
#export OBJCOPY=${CROSS_COMPILE}objcopy
#export OBJDUMP=${CROSS_COMPILE}objdump
#export STRIP=${CROSS_COMPILE}strip
#export PYTHONPATH=/workspace/images/arm64/beaglebone/beagleplay/crinit/build/bootloader/CORTEXA/scripts/dtc/pylibfdt:$PYTHONPATH

#if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/u-boot.img ] ; then
    if [ -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/bl31.bin ] ; then
        if [ -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tee-pager_v2.bin ] ; then
            echo "${CYAN}make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA $UBOOT_CFG_CORTEXA${NC}"
            make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA CROSS_COMPILE=$CC64 $UBOOT_CFG_CORTEXA
            
            #export CROSS_COMPILE=/workspace/sysroot_aarch64/bin/aarch64-linux-gnu-
            #export PATH=$PATH:/build/venv/bin
            #export PATH=/workspace/sysroot_aarch64/bin:$PATH

            echo "${CYAN}make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA BL31=${PROJECT_HOME}/${BOOTLOADER_DIR}/public/bl31.bin TEE=${PROJECT_HOME}/${BOOTLOADER_DIR}/public/${DEVICE}/tee-pager_v2.bin BINMAN_INDIRS=${PROJECT_HOME}/${BOOTLOADER_DIR}/ti-linux-firmware/${NC}"
            make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA CROSS_COMPILE=$CC64 BL31=${PROJECT_HOME}/${BOOTLOADER_DIR}/public/bl31.bin TEE=${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tee-pager_v2.bin BINMAN_INDIRS=${PROJECT_HOME}/${BOOTLOADER_DIR}/ti-linux-firmware/

            if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA/tispl.bin${SIGNED} ] ; then
                echo "Failure in u-boot CORTEXA build of [$UBOOT_CFG_CORTEXA]"
                ls -lha ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA/
                exit 2
            else
                cp -v ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA/tispl.bin${SIGNED} ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tispl.bin || true
                cp -v ${PROJECT_HOME}/${BOOTLOADER_DIR}/CORTEXA/u-boot.img${SIGNED} ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/u-boot.img || true
            fi
        else
            echo "${RED}Missing ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tee-pager_v2.bin${NC}"
            exit 2
        fi
    else
        echo "${RED}Missing ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/bl31.bin${NC}"
        exit 2
    fi
#else
#   echo "${BLUE}CORTEXA u-boot binary ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/u-boot.img already present${NC}"
#fi
