#!/usr/bin/env bash
set -e  # Stop on first error

echo "=============================="
echo " 🔨 OP-TEE Full Build Script"
echo "=============================="

# --------------------------------------------------
# Global Paths
# --------------------------------------------------

WORKSPACE=/workspace/images/arm64/nxp/frdm_imx93
BUILD_DIR=$WORKSPACE/optee/build
SYSROOT=/workspace/sysroot_aarch64
CROSS=aarch64-linux-gnu-

OPTEE_OS_EXPORT=$BUILD_DIR/optee_os/out/arm-plat-imx/export-ta_arm64
OPTEE_CLIENT_EXPORT=$BUILD_DIR/imx-optee-client/out/export/usr
SYSTEM_CONFIG=$WORKSPACE/systemd/system_config

# --------------------------------------------------
# Toolchain Vars
# --------------------------------------------------

export CROSS_COMPILE=$CROSS
export PKG_CONFIG_SYSROOT_DIR=$SYSROOT
export PKG_CONFIG_PATH=$SYSROOT/usr/lib/aarch64-linux-gnu/pkgconfig

# --------------------------------------------------
# 1️⃣ OP-TEE OS
# --------------------------------------------------
#mkdir -p "${BUILD_DIR}"
/${WORKSPACE}/optee/optee_os.sh "${BUILD_DIR}"
echo ">>> Building imx-optee-client"

# --------------------------------------------------
# 2️⃣ OP-TEE CLIENT
# --------------------------------------------------

cd $BUILD_DIR

if [ ! -d imx-optee-client ]; then
    git clone https://github.com/nxp-imx/imx-optee-client.git
fi

cd imx-optee-client

make CROSS_COMPILE=$CROSS \
     CFLAGS="--sysroot=$SYSROOT -I$SYSROOT/usr/include -I$SYSROOT/usr/include/aarch64-linux-gnu" \
     LIBRARY_PATH="$SYSROOT/usr/lib/aarch64-linux-gnu:$SYSROOT/usr/aarch64-linux-gnu/lib:$SYSROOT/lib/aarch64-linux-gnu" \
     C_INCLUDE_PATH="$SYSROOT/usr/include:$SYSROOT/usr/include/aarch64-linux-gnu" \
     PKG_CONFIG_PATH="$SYSROOT/usr/lib/aarch64-linux-gnu/pkgconfig" \
     LDFLAGS="--sysroot=$SYSROOT -L$SYSROOT/usr/lib/aarch64-linux-gnu -L$SYSROOT/usr/aarch64-linux-gnu/lib -L$SYSROOT/lib/aarch64-linux-gnu"

# Install into system_config
mkdir -p $SYSTEM_CONFIG
cp -R $OPTEE_CLIENT_EXPORT $SYSTEM_CONFIG/

# --------------------------------------------------
# 3️⃣ OP-TEE HELLO WORLD EXAMPLE
# --------------------------------------------------

echo ">>> Building optee_examples (hello world)"

cd $BUILD_DIR

if [ ! -d optee_examples ]; then
    git clone https://github.com/linaro-swg/optee_examples.git
fi

cd optee_examples
git checkout 3ef17eb

cd hello_world
# ---- Host App
make -C host CROSS_COMPILE=$CROSS TEEC_EXPORT=$OPTEE_CLIENT_EXPORT --no-builtin-variables

# ---- Trusted Application
make -C ta CROSS_COMPILE=$CROSS TA_DEV_KIT_DIR=$OPTEE_OS_EXPORT PLATFORM=arm-plat-imx O=out


# ---- Install TA + Host App
mkdir -p $SYSTEM_CONFIG/usr/lib/optee_armtz
cp ta/out/*.ta $SYSTEM_CONFIG/usr/lib/optee_armtz/

mkdir -p $SYSTEM_CONFIG/usr/bin
chmod +x host/optee_example_hello_world
cp host/optee_example_hello_world $SYSTEM_CONFIG/usr/bin/

# --------------------------------------------------
# 4️⃣ OP-TEE disk encryption key
# --------------------------------------------------

echo ">>> Building disk encryption key"
cd $WORKSPACE/optee/data_key
mkdir -p $WORKSPACE/optee/build/data_key
# ---- Host App
make -C host CROSS_COMPILE=$CROSS TEEC_EXPORT=$OPTEE_CLIENT_EXPORT --no-builtin-variables
mv host/optee_get_key ../build/data_key
mv host/optee_get_key.o ../build/data_key
# ---- Trusted Application
make -C ta CROSS_COMPILE=$CROSS TA_DEV_KIT_DIR=$OPTEE_OS_EXPORT PLATFORM=arm-plat-imx O=out
mv ta/out ../build/data_key

# ---- Install TA + Host App
mkdir -p $SYSTEM_CONFIG/usr/lib/optee_armtz
cp ../build/data_key/out/*.ta $SYSTEM_CONFIG/usr/lib/optee_armtz/

mkdir -p $SYSTEM_CONFIG/usr/bin
chmod +x ../build/data_key/optee_get_key
cp ../build/data_key/optee_get_key $SYSTEM_CONFIG/usr/bin/ # copy binary

# --------------------------------------------------
# 5️⃣ OP-TEE TEST (WI+6TH PKCS11 SUPPORT)
# --------------------------------------------------

echo ">>> Building imx-optee-test with PKCS11"

cd $BUILD_DIR

if [ ! -d imx-optee-test ]; then
    git clone https://github.com/nxp-imx/imx-optee-test.git
fi

cd imx-optee-test
git checkout 5b52b48a73b4cc3f228ec66ae6cf9920897bb2e6

# ---- Build TAs
make -C ta \
  CROSS_COMPILE=$CROSS \
  TA_DEV_KIT_DIR=$OPTEE_OS_EXPORT \
  O=out

# ---- Build supplicant plugins
make -C host/supp_plugin \
  CROSS_COMPILE=$CROSS \
  OPTEE_CLIENT_EXPORT=$OPTEE_CLIENT_EXPORT \
  O=out

# ---- xtest Build (YOUR EXACT COMMAND PRESERVED ✅)
make -C host/xtest V=1 \
  HOSTCC=aarch64-linux-gnu-gcc \
  CC=aarch64-linux-gnu-gcc \
  CROSS_COMPILE=aarch64-linux-gnu- \
  OPTEE_CLIENT_EXPORT=$OPTEE_CLIENT_EXPORT \
  OPTEE_OPENSSL_EXPORT=$SYSROOT/usr \
  TA_DEV_KIT_DIR=$OPTEE_OS_EXPORT \
  PKG_CONFIG_SYSROOT_DIR=$SYSROOT \
  PKG_CONFIG_PATH=$SYSROOT/usr/lib/aarch64-linux-gnu/pkgconfig \
  CFLAGS+="-DCFG_PKCS11_TA=1 -DCFG_PKCS11=1 -DCFG_PKCS11_TEST=1 -DCFG_REGRESSION_NXP=1 --sysroot=$SYSROOT \
          -I$SYSROOT/usr/include \
          -I$SYSROOT/usr/include/aarch64-linux-gnu \
          -I$OPTEE_OS_EXPORT/host_include \
          -I$BUILD_DIR/imx-optee-test/ta/bti_test/include \
          -I$BUILD_DIR/imx-optee-test/ta/concurrent/include \
          -I$BUILD_DIR/imx-optee-test/ta/create_fail_test/include \
          -I$BUILD_DIR/imx-optee-test/ta/crypt/include \
          -I$BUILD_DIR/imx-optee-test/ta/miss/include \
          -I$BUILD_DIR/imx-optee-test/ta/os_test/include \
          -I$BUILD_DIR/imx-optee-test/ta/rpc_test/include \
          -I$BUILD_DIR/imx-optee-test/ta/sims/include \
          -I$BUILD_DIR/imx-optee-test/ta/sims_keepalive/include \
          -I$BUILD_DIR/imx-optee-test/ta/supp_plugin/include \
          -I$BUILD_DIR/imx-optee-test/host/supp_plugin/include \
          -I$BUILD_DIR/imx-optee-test/host/xtest/adbg/include \
          -I$BUILD_DIR/imx-optee-client/libteec/include \
          -I$BUILD_DIR/imx-optee-test/ta/socket/include \
          -I$BUILD_DIR/imx-optee-test/ta/crypto_perf/include \
          -I$BUILD_DIR/imx-optee-test/ta/storage_benchmark/include \
          -I$BUILD_DIR/imx-optee-test/host/xtest \
          -I$BUILD_DIR/imx-optee-test/ta/include \
          -I$BUILD_DIR/imx-optee-test/ta/enc_fs/include \
          -I$BUILD_DIR/imx-optee-test/host/xtest/out/xtest \
          -I$BUILD_DIR/imx-optee-test/ta/concurrent_large/include \
          -I$BUILD_DIR/imx-optee-test/ta/large/include \
          -I$BUILD_DIR/imx-optee-test/ta/sdp_basic/include \
          -I$BUILD_DIR/imx-optee-test/ta/subkey1/include \
          -I$BUILD_DIR/imx-optee-test/ta/subkey2/include \
          -I$BUILD_DIR/imx-optee-client/out/export/usr/include \
          -I$BUILD_DIR/imx-optee-client/libckteec/include \
          -I$BUILD_DIR/imx-optee-test/ta/mp_sign/include \
          -I$BUILD_DIR/imx-optee-test/ta/tpm_log_test/include" \
  LDFLAGS="--sysroot=$SYSROOT \
         -L$BUILD_DIR/imx-optee-client/out/export/usr/lib \
         -L$SYSROOT/usr/lib/aarch64-linux-gnu \
         -lteec -lm -lckteec" \
  O=out xtest

cp host/xtest/out/xtest/xtest $SYSTEM_CONFIG/usr/bin/
cp -R ta/*/out/ta/*/*.ta $SYSTEM_CONFIG/usr/lib/optee_armtz/
cp -R ../optee_os/out/arm-plat-imx/ta/*/*.ta $SYSTEM_CONFIG/usr/lib/optee_armtz/

# --------------------------------------------------
# ✅ FINISHED
# --------------------------------------------------

echo "====================================="
echo " ✅ OP-TEE BUILD FULLY COMPLETE"
echo "====================================="
echo ""
echo "On target:"
echo "  /usr/sbin/tee-supplicant -d --ta-path=/usr/lib/optee_armtz & "
echo "  /usr/bin/optee_example_hello_world "
echo "  xtest "
echo ""
