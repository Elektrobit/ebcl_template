#!/bin/sh

. "${PWD}/../bootloader/bootloader_env.sh"


if [ ! -d ${PROJECT_HOME}/${TOOLCHAIN_DIR}/ ] ; then
    ./../gcc/gcc.sh
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

./../bootloader/bootloader_tfa.sh
./../bootloader/bootloader_optee.sh
./../bootloader/bootloader_uboot_cortexR.sh
./../bootloader/bootloader_uboot_cortexA.sh

cp ./../bootloader/extlinux.conf ${PROJECT_HOME}/${BOOTLOADER_DIR}/public/