#!/bin/bash
set -e

# === CONFIGURATION ===
PROJECT_HOME=${PWD}
OUTPUT_KERNEL=../kernel/build
KERNEL_DIR=linux-imx-d23d64eea5111e1607efcce1d601834fceec92cb
KERNEL_URL="https://github.com/nxp-imx/linux-imx/archive/d23d64eea5111e1607efcce1d601834fceec92cb.tar.gz"
CROSS_COMPILE="aarch64-linux-gnu-"
ARCH="arm64"
SYSROOT="/workspace/sysroot_aarch64"
JOBS=$(nproc)

mkdir -p ${OUTPUT_KERNEL}
cd ${OUTPUT_KERNEL}

# === STEP 1: Download & extract kernel ===
if [ ! -d "$KERNEL_DIR" ]; then
    echo "📦 Downloading Linux kernel..."
    wget -qO- "$KERNEL_URL" | tar -xz
fi

cd "$KERNEL_DIR"

# === STEP 2: Apply defconfig ===
make ARCH=$ARCH CROSS_COMPILE=$CROSS_COMPILE O=${PROJECT_HOME}/${OUTPUT_KERNEL}/linux_build imx_v8_defconfig

echo "➕ Enabling dm-verity ..."
cp ../../patch/.config ${PROJECT_HOME}/${OUTPUT_KERNEL}/linux_build/.config

# === STEP 3: Build with Yocto-equivalent flags ===
KCFLAGS="-fno-pic \
-march=armv8-a+crc+crypto \
-mtune=cortex-a55 \
-mgeneral-regs-only \
-mabi=lp64 \
-fno-strict-aliasing \
-fno-common \
-fshort-wchar \
-fno-omit-frame-pointer \
-fno-optimize-sibling-calls \
-fno-pie \
-fno-strict-overflow \
-Wall -Wundef -Werror=strict-prototypes \
-Wno-trigraphs \
-Werror=implicit-function-declaration \
-Werror=implicit-int \
-Werror=return-type \
-Wno-format-security \
-std=gnu11 \
-fstack-protector-strong \
-O2 \
-pipe \
-g \
-D_FORTIFY_SOURCE=2 \
--sysroot=${SYSROOT}"

make -j$JOBS \
  ARCH=$ARCH \
  CROSS_COMPILE=$CROSS_COMPILE \
  KCFLAGS="$KCFLAGS" \
  O=${PROJECT_HOME}/${OUTPUT_KERNEL}/linux_build \
  Image dtbs modules
