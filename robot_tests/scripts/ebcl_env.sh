#!/bin/bash
#
# Copyright (c) Elektrobit Automotive GmbH. All rights reserved.
#
# ------------------------------------------------------------------------------

WORKSPACE="$(dirname $(dirname $(realpath "$0")))"
echo "WORKSPACE: ${WORKSPACE}"

test_lib_folder="${WORKSPACE}/lib/"

if [[ -z "${PYTHONPATH:-}" ]]; then
    PYTHONPATH=""
    export PYTHONPATH="${test_lib_folder}"
elif [[ ":$PYTHONPATH:" != *":${test_lib_folder}:"* ]]; then
    export PYTHONPATH="${test_lib_folder}:${PYTHONPATH}"
fi

echo "PYTHONPATH: ${PYTHONPATH}"

EBCL_TF_BUILD_MODE="Download"
export EBCL_TF_BUILD_MODE
echo "Image will be downloaded from artifactory"

EBCL_TF_IMAGE_BASE="${WORKSPACE}/downloaded_images"
echo "Downloaded images will be stored into "${EBCL_TF_IMAGE_BASE}
export EBCL_TF_IMAGE_BASE
echo "EBCL_TF_IMAGE_BASE: ${EBCL_TF_IMAGE_BASE}"
EBCL_TF_POWER_MODE="QEMU_EXPLICT_OPTION"
export EBCL_TF_POWER_MODE


EBCL_TC_IMAGE="standard/arm64"
export EBCL_TC_IMAGE
echo "EBCL_TC_IMAGE: ${EBCL_TC_IMAGE}"

: "${ARTIFACTORY_USER:=}"
: "${ARTIFACTORY_IDENTITY_TOKEN:=}"
if [ -z "${ARTIFACTORY_USER}" ] || [ -z "${ARTIFACTORY_IDENTITY_TOKEN}" ]; then
    ARTIFACTORY_IDENTITY_TOKEN_FILE="${WORKSPACE}/.netrc"
    export ARTIFACTORY_IDENTITY_TOKEN_FILE
fi
# Artifactory paths
EBCL_IMAGE_BASE_ARTIFACTORY="https://artifactory.elektrobit.com/artifactory/eb_corbos_linux_sandbox-snapshots-generic/sdk_prebuilt_images"
EBCL_IMAGE_BUNDLE_PATH="${EBCL_TC_IMAGE}"
EBCL_IMAGE_BUNDLE_NAME="build.tar.xz"
EBCL_IMAGE_BUNDLE_URL="${EBCL_IMAGE_BASE_ARTIFACTORY}/${EBCL_IMAGE_BUNDLE_PATH}/${EBCL_IMAGE_BUNDLE_NAME}"
export EBCL_IMAGE_BUNDLE_URL

FORCE_CLEAN_REBUILD="1"
export FORCE_CLEAN_REBUILD

# QEMU COMMAND FOR ARM64
if [[ "${EBCL_IMAGE_BUNDLE_URL}" == *"arm64"* ]]; then
    echo "Image type is the supported arm64."
else
    echo "Image type is not arm64, not supported yet."
    exit 1
fi

EBCL_TC_QEMU_NETWORK_APPEND="ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3"
export EBCL_TC_QEMU_NETWORK_APPEND
EBCL_TC_QEMU_KERNEL_CMDLINE="console=ttyAMA0"
export EBCL_TC_QEMU_KERNEL_CMDLINE
EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND="rw"
export EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND

# Test Image (? set by the test case)
if [[ "${EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND}" == *"verity"* ]]; then
    EBCL_ROOT_IMAGE_FILE_NAME="image.verity.raw"
else
    EBCL_ROOT_IMAGE_FILE_NAME="image.raw"
fi
export EBCL_ROOT_IMAGE_FILE_NAME

EBCL_KERNEL_FILE_NAME="vmlinuz"
EBCL_INITRD_FILE_NAME="initrd.img"

EBCL_STORAGE_DIRECTORY="${EBCL_TF_IMAGE_BASE}/${EBCL_IMAGE_BUNDLE_PATH}"
EBCL_ROOT_IMAGE="${EBCL_STORAGE_DIRECTORY}/${EBCL_ROOT_IMAGE_FILE_NAME}"
export EBCL_ROOT_IMAGE
EBCL_KERNEL="${EBCL_STORAGE_DIRECTORY}/${EBCL_KERNEL_FILE_NAME}"
export EBCL_KERNEL
EBCL_INITRD="${EBCL_STORAGE_DIRECTORY}/${EBCL_INITRD_FILE_NAME}"
export EBCL_INITRD

# tests run by default
#TEST_SUITE="ebcl_base"
#export TEST_SUITE

# Introduce as a template
EBCL_QEMU_CMDLINE_AARCH64='qemu-system-aarch64
    -machine virt -cpu cortex-a72 -machine type=virt -nographic -m 4G
    -netdev user,id=mynet0,${EBCL_TC_QEMU_NETWORK_APPEND}
    -device virtio-net-pci,netdev=mynet0
    -kernel "${EBCL_KERNEL}"
    -append "${EBCL_TC_QEMU_KERNEL_CMDLINE} ${EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND} test_overlay=/dev/vdb"
    -initrd "${EBCL_INITRD}"
    -drive format=raw,file=${EBCL_ROOT_IMAGE},if=virtio'
# todo, addtional overlay will be added in test cases, by append new line.

EBCL_QEMU_CMDLINE="${EBCL_QEMU_CMDLINE_AARCH64}"
export EBCL_QEMU_CMDLINE
echo "EBCL_QEMU_CMDLINE: ${EBCL_QEMU_CMDLINE}"

# COMMAND FOR SHUTDOWN IN IMAGE
export EBCL_TC_SHUTDOWN_COMMAND="crinit-ctl poweroff"
export EBCL_TC_SHUTDOWN_TARGET="Power down"

# EBCL_TF_CLEAR_CMD="task mrproper"
