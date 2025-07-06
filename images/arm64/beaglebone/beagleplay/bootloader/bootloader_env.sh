#!/bin/sh

PROJECT_HOME=${PWD}
OUTPUT_BOOTLOADER=../bootloader/build
OUTPUT_GCC=../gcc/build/out
OUTPUT_KERNEL=../kernel/build
DOWNLOAD_DIR=${OUTPUT_GCC}/download
TOOLCHAIN_DIR=${OUTPUT_GCC}/toolchain
BOOTLOADER_DIR=${OUTPUT_BOOTLOADER}
KERNEL_DIR=${OUTPUT_KERNEL}


RED='\033[0;31m'
BLUE='\033[0;34m'
ORANGE='\033[31;1m' # warning
BLUE='\033[0;34m' # result
CYAN='\033[0;36m' # info
NC='\033[0m' # No Color

 # default
#CC32=arm-linux-gnueabihf-
CC32=${PROJECT_HOME}/${TOOLCHAIN_DIR}/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
CC64=${PROJECT_HOME}/${TOOLCHAIN_DIR}/arm-gnu-toolchain-14.2.rel1-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-
#CC64=/workspace/sysroot_aarch64/bin/aarch64-linux-gnu-

#beagleplay
SOC_NAME=am62x
SECURITY_TYPE=gp
SIGNED=_unsigned
TFA_BOARD=lite
OPTEE_PLATFORM="k3-am62x"
OPTEE_EXTRA_ARGS="CFG_WITH_SOFTWARE_PRNG=y"
UBOOT_CFG_CORTEXR="am62x_beagleplay_r5_defconfig"
UBOOT_CFG_CORTEXA="am62x_beagleplay_a53_defconfig"
TI_FIRMWARE="10.01.10"
TRUSTED_FIRMWARE="v2.12.0"
OPTEE="4.4.0"
UBOOT="v2025.01-Beagle"

if [ ! "${CORES}" ] ; then
	CORES=$(($(getconf _NPROCESSORS_ONLN) * 2)) # cores and thread
fi

