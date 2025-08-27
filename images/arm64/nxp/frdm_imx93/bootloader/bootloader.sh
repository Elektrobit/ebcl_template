#!/bin/bash
. "/workspace/images/arm64/nxp/frdm_imx93/bootloader/frdm_imx93_env.sh"

#ls -la ${PROJECT_HOME}/${BOOTLOADER_DIR}/${MKIMG_DIR}/iMX93/flash.bin
#read -p "Press enter to continue"
if [ ! -f ${PROJECT_HOME}/${BOOTLOADER_DIR}/${MKIMG_DIR}/iMX93/flash.bin ]; then
  mkdir -p ${PROJECT_HOME}/${BOOTLOADER_DIR}

  cd ${PROJECT_HOME}/${BOOTLOADER_DIR}

  # === Step 1: Clone and patch U-Boot ===
  if [ ! -d "$UBOOT_DIR" ]; then
      echo "📦 Cloning U-Boot from NXP..."
      git clone "$UBOOT_REPO" "$UBOOT_DIR"
      cd "$UBOOT_DIR"
      echo "🔀 Checking out U-Boot commit: $UBOOT_HASH"
      git fetch --all
      git checkout "$UBOOT_HASH" -b "$UBOOT_HASH" || git checkout "$UBOOT_HASH"
      echo "📌 Applying U-Boot FRDM patches..."
      git am "$PATCHES_DIR"/0002-*.patch
      git am "$PATCHES_DIR"/0003-*.patch || echo "✅ 0003 skipped (optional)"
      git am "$PATCHES_DIR"/0004-*.patch || echo "✅ 0004 skipped (partial patch for i.MX91)"
      cd ..
  fi

  # === Step 2: Build TF-A ===
  if [ ! -d "$ATF_DIR" ]; then
      echo "🛠️ Cloning TF-A..."
      git clone "$ATF_REPO" "$ATF_DIR"
  fi

  cd "$ATF_DIR"
  git clean -fdx
  git reset --hard
  git fetch --all
  git checkout "$ATF_COMMIT"

  echo "🔨 Building TF-A (bl31)..."
  make -j$(nproc) \
    CROSS_COMPILE="${CROSS_COMPILE}" \
    PLAT=imx93 \
    LD="${CROSS_COMPILE}ld" \
    CC="${CROSS_COMPILE}gcc" \
    IMX_BOOT_UART_BASE= DEBUG=0 \
    BUILD_BASE=build-optee \
    SPD=opteed \
    bl31

  cp build-optee/imx93/release/bl31.bin ../$UBOOT_DIR/
  cd ..

  # === Step 3: Build OP-TEE ===
  if [ ! -d "$OPTEE_DIR" ]; then
      echo "🔧 Cloning OP-TEE..."
      git clone "$OPTEE_REPO" "$OPTEE_DIR"
  fi

  cd "$OPTEE_DIR"
  git clean -fdx
  git reset --hard
  git fetch --all
  git checkout "$OPTEE_COMMIT"

  echo "🔨 Building OP-TEE (tee.bin)..."
  sudo apt update
  sudo apt install libgnutls28-dev u-boot-tools -y 
  python3 -m venv venv
  source venv/bin/activate
  pip install cryptography pyelftools

  make -j$(nproc) -C . \
    PLATFORM=imx-mx93evk \
    O="${OPTEE_BUILD_DIR}" \
    ARCH=arm \
    CFG_ARM64_core=y \
    CFG_TEE_CORE_LOG_LEVEL=0 \
    CFG_TEE_TA_LOG_LEVEL=0 \
    COMPILER=gcc \
    CROSS_COMPILE64="${CROSS_COMPILE}" \
    CROSS_COMPILE_core="${CROSS_COMPILE}" \
    CROSS_COMPILE_ta_arm64="${CROSS_COMPILE}" \
    OPTEE_CLIENT_EXPORT="${SYSROOT}/usr" \
    TEEC_EXPORT="${SYSROOT}/usr" \
    CFLAGS="--sysroot=${SYSROOT} -march=armv8-a+crc+crypto" \
    LDFLAGS="--sysroot=${SYSROOT} -L${LIBGCC_DIR}" \
    NOWERROR=1

  cp "$OPTEE_BUILD_DIR/core/tee-raw.bin" ../$UBOOT_DIR/tee.bin
  cd ..

  # === Step 4: Build U-Boot ===
  cd "$UBOOT_DIR"
  echo "⚙️  Configuring U-Boot with patched FRDM defconfig..."
  make distclean
  make imx93_11x11_frdm_defconfig

  echo "🏗️  Building U-Boot..."
  make -j$(nproc) CROSS_COMPILE=${CROSS_COMPILE}

  echo "✅ U-Boot build (with bl31.bin and tee.bin) complete."
  cd ..

  # === Step 5: mkimage ===
  if [ ! -d "$MKIMG_DIR" ]; then
    git clone https://github.com/nxp-imx/imx-mkimage.git "$MKIMG_DIR"
    cd "$MKIMG_DIR"
    git checkout "$MKIMG_COMMIT"
  else
    cd "$MKIMG_DIR"
    git checkout "$MKIMG_COMMIT"
    git clean -fdx
  fi
  pwd
  cp ${PROJECT_HOME}/${BOOTLOADER_DIR}/../patch/lpddr* iMX93
  cp ${PROJECT_HOME}/${BOOTLOADER_DIR}/../patch/mx93a1-ahab-container.img iMX93
  cp ${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/spl/u-boot-spl.bin iMX93
  cp ${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/u-boot.bin iMX93
  cp ${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/bl31.bin iMX93
  cp ${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/tee.bin iMX93
  make SOC=iMX93 flash_singleboot TEE=tee.bin

  echo "🎉 All components built successfully!"
else
  echo "flash.bin already exist!"
fi
