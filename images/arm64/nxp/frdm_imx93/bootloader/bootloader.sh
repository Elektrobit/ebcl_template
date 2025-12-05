#!/bin/bash
set -euo pipefail

. "/workspace/images/arm64/nxp/frdm_imx93/bootloader/frdm_imx93_env.sh"

mkdir -p "${PROJECT_HOME}/${BOOTLOADER_DIR}"
cd "${PROJECT_HOME}/${BOOTLOADER_DIR}"
#if [ ! -f "${PROJECT_HOME}/${BOOTLOADER_DIR}/${MKIMG_DIR}/iMX93/flash.bin" ]; then
if [ ! -f "${PROJECT_HOME}/${BOOTLOADER_DIR}/${MKIMG_DIR}/iMX93/flash.bin" ]; then

  # === Step 1: Clone and patch U-Boot ===
  if [ ! -d "${UBOOT_DIR}" ]; then
    echo "📦 Cloning U-Boot from NXP..."
    git clone "${UBOOT_REPO}" "${UBOOT_DIR}"
    pushd "${UBOOT_DIR}"
      echo "🔀 Checking out U-Boot commit: ${UBOOT_HASH}"
      git fetch --all
      git checkout "${UBOOT_HASH}" -b "${UBOOT_HASH}" || git checkout "${UBOOT_HASH}"
      echo "📌 Applying U-Boot FRDM patches..."
      git am "${PATCHES_DIR}"/0002-*.patch
      git am "${PATCHES_DIR}"/0003-*.patch || echo "✅ 0003 skipped (optional)"
      git am "${PATCHES_DIR}"/0004-*.patch || echo "✅ 0004 skipped (partial patch for i.MX91)"
      git apply "${PATCHES_DIR}"/signature.patch
    popd
  fi

  # === Step 2: Build TF-A ===
  if [ ! -d "${ATF_DIR}" ]; then
    echo "🛠️ Cloning TF-A..."
    git clone "${ATF_REPO}" "${ATF_DIR}"
  fi

  pushd "${ATF_DIR}"
    git clean -fdx
    git reset --hard
    git fetch --all
    git checkout "${ATF_COMMIT}"

    echo "🔨 Building TF-A (bl31)..."
    make -j"$(nproc)" \
      CROSS_COMPILE="${CROSS_COMPILE}" \
      PLAT=imx93 \
      LD="${CROSS_COMPILE}ld" \
      CC="${CROSS_COMPILE}gcc" \
      IMX_BOOT_UART_BASE= DEBUG=0 \
      BUILD_BASE=build-optee \
      SPD=opteed \
      bl31

    cp build-optee/imx93/release/bl31.bin "../${UBOOT_DIR}/"
  popd
  
   # === Step 3: Build OP-TEE ===
  /${PROJECT_HOME}/../optee/optee_os.sh .
  cp "${OPTEE_DIR}/${OPTEE_BUILD_DIR}/core/tee-raw.bin" "${UBOOT_DIR}/tee.bin"
fi

 # === Step 4: Configure u-boot, generate boot.scr and inject keys ===
pushd "${UBOOT_DIR}"
  echo "⚙️  Configuring U-Boot with patched FRDM defconfig..."
  make distclean
  make  imx93_11x11_frdm_defconfig

  echo "➕ Enabling FIT + script + signature support and auto-boot command..."
  # Enable FIT & signatures
  scripts/config --enable CONFIG_FIT
  scripts/config --enable CONFIG_FIT_VERBOSE
  # !LINKSTO EBCL-REQ-SWRS-01, 1
  scripts/config --enable CONFIG_FIT_SIGNATURE
  scripts/config --enable CONFIG_RSA
  scripts/config --enable CONFIG_FIT_SCRIPT
  scripts/config --enable CONFIG_CMD_SOURCE
  scripts/config --enable CONFIG_FIT_RSASSA_PSS || true
  scripts/config --enable CONFIG_OF_CONTROL
  #scripts/config --disable CONFIG_LEGACY_IMAGE_FORMAT
  scripts/config --enable CONFIG_FIT_FULL_CHECK
  scripts/config --enable CONFIG_FIT_PRINT

  # Set boot delay and boot command (mmc1, load FIT, source embedded script)
  scripts/config --set-val CONFIG_BOOTDELAY 3
  scripts/config --set-str CONFIG_BOOTCOMMAND \
      "mmc dev 1; fatload mmc 1:1 0x90000000 fitA.itb; setenv script_addr 0x83100000; imxtract 0x90000000 bootscr \${script_addr}; source \${script_addr}"

  make olddefconfig
  #echo "🔨 make tools for u-boot"
  #make CROSS_COMPILE="${CROSS_COMPILE}" HOSTCC=gcc tools
  echo "🏗️  Building U-Boot (first pass, no key yet)..."
  make -j"$(nproc)" CROSS_COMPILE="${CROSS_COMPILE}"

  ### Create boot script FIT subimage
  echo "🔑 Generating boot.scr..."
  mkimage \
      -A arm64 -T script -C none -n "EB FIT boot script" \
      -d ${PROJECT_HOME}/build/boot.cmd ${PROJECT_HOME}/build/boot.scr

  ### Embed public key for FIT verification
  echo "🔑 Embedding public key into U-Boot DT..."
  cp u-boot.dtb u-boot_noKey.dtb

  echo -e "${CYAN}Dump the u-boot.dtb BEFORE key insert${NC}"
  dtc -I dtb -O dts u-boot.dtb | grep -A5 ubootkey || echo "⚠️ No key yet (expected)"
  negative_test=false;
  if [ "$negative_test" = "true" ]; then
      # !LINKSTO EBCL-REQ-SWRS-09, 1
      #create u-boot.dtb and fit.itb with keyC
      mkimage -f ${PROJECT_HOME}/build/frdm_imx93_fit.its -K u-boot.dtb -k ${PROJECT_HOME}/../keysB -r ${PROJECT_HOME}/${BOOTLOADER_DIR}/fitB.itb
      #create u-boot_keysB.dtb renaming u-boot.dtb
      mv u-boot.dtb u-boot_keysB.dtb
      #restore the no key dtb u-boot_noKey.dtb as u-boot.dtb
      cp u-boot_noKey.dtb u-boot.dtb
      #remove the fit signded with keyC
      rm ${PROJECT_HOME}/${BOOTLOADER_DIR}/fitB.itb
      #create u-boot.dtb and fit.itb with normal key
      mkimage -f ${PROJECT_HOME}/build/frdm_imx93_fit.its -K ${PROJECT_HOME}/${BOOTLOADER_DIR}/${UBOOT_DIR}/u-boot.dtb -k ${PROJECT_HOME}/../keysA -r ${PROJECT_HOME}/${BOOTLOADER_DIR}/fitA.itb
      mv u-boot.dtb u-boot_keysA.dtb 
      cp u-boot_keysB.dtb u-boot.dtb
  else
      # !LINKSTO EBCL-REQ-SWRS-10, 1
      echo "➡️  Running mkimage to inject key"
      mkimage \
          -f ${PROJECT_HOME}/build/frdm_imx93_fit.its \
          -K ${PROJECT_HOME}/${BOOTLOADER_DIR}/${UBOOT_DIR}/u-boot.dtb \
          -k ${PROJECT_HOME}/../keysA \
          -r ${PROJECT_HOME}/${BOOTLOADER_DIR}/fitA.itb
  fi
  echo -e "${CYAN}Dump the u-boot.dtb AFTER key insert...${NC}"
  dtc -I dtb -O dts u-boot.dtb | grep -A10 ubootkey || echo "❌ Key not found!"
  echo -e "${CYAN}Dump the u-boot.dtb AFTER key inserts... DONE${NC}"

  cp u-boot.dtb arch/arm/dts/u-boot.dtb
  make EXT_DTB=u-boot.dtb CROSS_COMPILE="${CROSS_COMPILE}" u-boot.bin
  #cat u-boot_nokey.bin u-boot.dtb > u-boot.bin
  #./tools/binman/binman replace -i u-boot_nokey.bin -f u-boot.dtb u-boot-dtb

  echo "📖 Checking key presence inside final DTB..."
  dtc -I dtb -O dts u-boot.dtb | grep -A10 ubootkey || echo "⚠️ Key not found!"

  echo "✅ U-Boot build (with bl31.bin, tee.bin, and public key) complete."
popd

# === Step 5: Build flash.bin (imx-mkimage) ===
if [ ! -d "${MKIMG_DIR}" ]; then
  git clone https://github.com/nxp-imx/imx-mkimage.git "${MKIMG_DIR}"
  pushd "${MKIMG_DIR}"
    git checkout "${MKIMG_COMMIT}"
  popd
else
  pushd "${MKIMG_DIR}"
    git checkout "${MKIMG_COMMIT}"
    git clean -fdx
  popd
fi

pushd "${MKIMG_DIR}"
  pwd
  cp "${PROJECT_HOME}/${BOOTLOADER_DIR}/../patch"/lpddr* iMX93/
  cp "${PROJECT_HOME}/${BOOTLOADER_DIR}/../patch/mx93a1-ahab-container.img" iMX93/
  cp "${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/spl/u-boot-spl.bin" iMX93/
  cp "${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/u-boot.bin" iMX93/
  cp "${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/bl31.bin" iMX93/
  cp "${PROJECT_HOME}/${BOOTLOADER_DIR}/uboot-imx/tee.bin" iMX93/
  make SOC=iMX93 flash_singleboot TEE=tee.bin
popd

echo "🎉 All components built successfully!"
#else
#  echo "flash.bin already exist!"
#fi
