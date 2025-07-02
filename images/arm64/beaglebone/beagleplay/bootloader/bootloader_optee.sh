#!/bin/sh

. "${PWD}/../bootloader/bootloader_env.sh"

#export LD_LIBRARY_PATH=/workspace/sysroot_aarch64/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
#export PATH=/workspace/sysroot_aarch64/bin:$PATH
#export AS=aarch64-linux-gnu-as
#export PYTHON3=/build/venv/bin/python3
#export PATH=/build/venv/bin:$PATH

#if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tee-pager_v2.bin ] ; then
    if [ ! -d ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee_os/ ] ; then
        echo "${CYAN}git clone -b ${OPTEE} https://github.com/OP-TEE/optee_os.git${NC}"
        git clone -b ${OPTEE} https://github.com/OP-TEE/optee_os.git --depth=10 ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee_os/
    fi
    echo "${CYAN}make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee_os/ -j${CORES} O=.${PROJECT_HOME}/${BOOTLOADER_DIR}/optee CROSS_COMPILE=$CC32 CROSS_COMPILE64=$CC64 CFLAGS= LDFLAGS= CFG_ARM64_core=y $OPTEE_EXTRA_ARGS PLATFORM=${OPTEE_PLATFORM} all${NC}"
    make -C ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee_os/ -j${CORES} O=${PROJECT_HOME}/${BOOTLOADER_DIR}/optee CROSS_COMPILE=$CC32 CROSS_COMPILE64=$CC64 CFLAGS= LDFLAGS= CFG_ARM64_core=y $OPTEE_EXTRA_ARGS PLATFORM=${OPTEE_PLATFORM} all

    if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee/core/tee-pager_v2.bin ] ; then
        echo "${RED}Failure in ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee{NC}"
        ls -lha ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee/
        exit 2
    else
        cp -v ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee/core/tee-pager_v2.bin ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/
    fi

    echo "${CYAN}rm -rf ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee${NC}"
    #rm -rf ${PROJECT_HOME}/${BOOTLOADER_DIR}/optee/ || true
#else
#    echo "${BLUE}optee binary ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/tee-pager_v2.bin already present${NC}"
#fi
