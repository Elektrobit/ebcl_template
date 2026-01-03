#!/bin/bash
set -euo pipefail

OPTEE_REPO="https://github.com/nxp-imx/imx-optee-os.git"
OPTEE_COMMIT="612bc5a642a4608d282abeee2349d86de996d7ee"
OPTEE_DIR="optee_os"
OPTEE_BUILD_DIR="out/arm-plat-imx"
SYSROOT=/workspace/sysroot_aarch64/
CROSS_COMPILE=aarch64-linux-gnu-
LIBGCC_DIR="${SYSROOT}/lib/gcc/aarch64-linux-gnu/11"

echo "path ${1}"
mkdir -p "${1}"
cd "${1}"

if [ ! -d "${SYSROOT}usr" ]; then
  echo "⚠️  ${SYSROOT}usr not found, please build it first: make sysroot_install"
  exit 1
fi

if [ ! -f "${OPTEE_BUILD_DIR}/core/tee-raw.bin" ]; then
  # === Step 1️⃣: Build OP-TEE ===
  if [ ! -d "${OPTEE_DIR}" ]; then
    echo "🔧 Cloning OP-TEE..."
    git clone "${OPTEE_REPO}" "${OPTEE_DIR}"
  fi

  pushd "${OPTEE_DIR}"
    git clean -fdx
    #git reset --hard
    git fetch --all
    git checkout "${OPTEE_COMMIT}"

    echo "🔨 Building OP-TEE (tee.bin)..."
    #python3 -m venv venv
    # shellcheck disable=SC1091
    #source venv/bin/activate
    #pip install cryptography pyelftools
#      CFG_TEE_CORE_LOG_LEVEL=4 \
#      CFG_TEE_TA_LOG_LEVEL=3 \
#      CFG_TA_DEBUG=y \
    make -j"$(nproc)" -C . \
      PLATFORM=imx-mx93evk \
      O="${OPTEE_BUILD_DIR}" \
      ARCH=arm \
      CFG_ARM64_core=y \
      CFG_RPMB_FS=y \
      CFG_RPMB_WRITE_KEY=y \
      CFG_REE_FS=n \
      COMPILER=gcc \
      CROSS_COMPILE64="${CROSS_COMPILE}" \
      CROSS_COMPILE_core="${CROSS_COMPILE}" \
      CROSS_COMPILE_ta_arm64="${CROSS_COMPILE}" \
      OPTEE_CLIENT_EXPORT="${SYSROOT}/usr" \
      TEEC_EXPORT="${SYSROOT}/usr" \
      CFLAGS="--sysroot=${SYSROOT} -march=armv8-a+crc+crypto" \
      LDFLAGS="--sysroot=${SYSROOT} -L${LIBGCC_DIR}" \
      NOWERROR=1
  popd
else
  echo "${OPTEE_BUILD_DIR}/core/tee-raw.bin present"
fi
