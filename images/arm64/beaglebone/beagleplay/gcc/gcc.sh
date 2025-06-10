#!/bin/sh

. "${PWD}/../bootloader/bootloader_env.sh"

echo "andor ${DOWNLOAD_DIR}"
echo "andor ${PROJECT_HOME}"
mkdir -p ${DOWNLOAD_DIR}
mkdir -p ${TOOLCHAIN_DIR}
cd ${PROJECT_HOME}/${DOWNLOAD_DIR}
pwd
echo "${BLUE}download 32bit arm-none-linux-gnueabihf. toolchain to ${PROJECT_HOME}/${DOWNLOAD_DIR}${NC}"
wget -c https://developer.arm.com/-/media/Files/downloads/gnu/14.2.rel1/binrel/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-linux-gnueabihf.tar.xz
wget -c http://sources.buildroot.net/toolchain-external-arm-aarch64/arm-gnu-toolchain-14.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz
wget -c https://releases.linaro.org/components/toolchain/binaries/latest-7/aarch64-linux-gnu/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu.tar.xz
tar xf arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-linux-gnueabihf.tar.xz -C ${PROJECT_HOME}/${TOOLCHAIN_DIR}
tar xf arm-gnu-toolchain-14.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz -C ${PROJECT_HOME}/${TOOLCHAIN_DIR}
tar xf gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu.tar.xz -C ${PROJECT_HOME}/${TOOLCHAIN_DIR}
cd ${PROJECT_HOME}

