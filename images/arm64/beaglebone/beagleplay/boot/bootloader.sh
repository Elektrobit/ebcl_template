#!/bin/sh

. "${PWD}/../boot/bootloader_env.sh"


if [ ! -d ${PROJECT_HOME}/${TOOLCHAIN_DIR}/ ] ; then
    mkdir -p ${DOWNLOAD_DIR}
    mkdir -p ${TOOLCHAIN_DIR}
    cd ${PROJECT_HOME}/${DOWNLOAD_DIR}
    pwd
    echo "${BLUE}download 32bit arm-none-linux-gnueabihf. toolchain to ${PROJECT_HOME}/${DOWNLOAD_DIR}${NC}"
    wget -c https://developer.arm.com/-/media/Files/downloads/gnu/14.2.rel1/binrel/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-linux-gnueabihf.tar.xz
    wget -c http://sources.buildroot.net/toolchain-external-arm-aarch64/arm-gnu-toolchain-14.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz
    tar xf arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-linux-gnueabihf.tar.xz -C ${PROJECT_HOME}/${TOOLCHAIN_DIR}
    tar xf arm-gnu-toolchain-14.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz -C ${PROJECT_HOME}/${TOOLCHAIN_DIR}
    cd ${PROJECT_HOME}
else
     echo "${ORANGE}${TOOLCHAIN_DIR} folder exist no toolchain will be extracted${NC}"
fi

mkdir -p ${PROJECT_HOME}/${BOOTLOADER_DIR}

#if [ -d ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot/ ] ; then
#    rm -rf ${PROJECT_HOME}/${BOOTLOADER_DIR}/u-boot/
#fi

mkdir -p ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/

sudo apt install -y swig python3-dev libgnutls28-dev
sudo chown -R $(whoami):$(whoami) /build/venv
pip install yamllint jsonschema pyelftools

./../boot/bootloader_tfa.sh
./../boot/bootloader_optee.sh
./../boot/bootloader_uboot_cortexR.sh
./../boot/bootloader_uboot_cortexA.sh
