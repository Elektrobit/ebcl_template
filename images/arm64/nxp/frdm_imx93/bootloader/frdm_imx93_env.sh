#!/bin/sh
echo "configuration..."

PROJECT_HOME=${PWD}
OUTPUT_BOOTLOADER=../bootloader/build
OUTPUT_GCC=../gcc/build/out

DOWNLOAD_DIR=${OUTPUT_GCC}/download
TOOLCHAIN_DIR=${OUTPUT_GCC}/toolchain
BOOTLOADER_DIR=${OUTPUT_BOOTLOADER}

RED='\033[0;31m'
BLUE='\033[0;34m'
ORANGE='\033[31;1m' # warning
BLUE='\033[0;34m' # result
CYAN='\033[0;36m' # info
NC='\033[0m' # No Color

# === Configuration ===
SYSROOT=/workspace/sysroot_aarch64/
CROSS_COMPILE=aarch64-linux-gnu-
LIBGCC_DIR="${SYSROOT}/lib/gcc/aarch64-linux-gnu/11"
UBOOT_REPO="https://github.com/nxp-imx/uboot-imx.git"
UBOOT_HASH="de16f4f1722"
UBOOT_DIR="uboot-imx"
PATCHES_DIR="/workspace/images/arm64/nxp/frdm_imx93/bootloader/patch"
ATF_REPO="https://github.com/nxp-imx/imx-atf.git"
ATF_COMMIT="28affcae957cb8194917b5246276630f9e6343e1"
ATF_DIR="imx-atf"

OPTEE_REPO="https://github.com/nxp-imx/imx-optee-os.git"
OPTEE_COMMIT="612bc5a642a4608d282abeee2349d86de996d7ee"
OPTEE_DIR="optee_os"
OPTEE_BUILD_DIR="out/arm-plat-imx"

MKIMG_REPO="https://github.com/nxp-imx/imx-mkimage.git"
MKIMG_COMMIT="4c2e5b25232f5aa003976ddca9d1d2fb9667beb1"
MKIMG_DIR="imx-mkimage"

echo "configuration END"