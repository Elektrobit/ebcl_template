#!/bin/bash
#
# Copyright (c) Elektrobit Automotive GmbH. All rights reserved.
#
# ------------------------------------------------------------------------------

: "${WORKSPACE:=$(dirname $(dirname $(realpath "$0")))}"
echo "WORKSPACE: ${WORKSPACE}"

EBCL_TF_BUILD_MODE="Download"
export EBCL_TF_BUILD_MODE
echo "EBCL_TF_BUILD_MODE: ${EBCL_TF_BUILD_MODE}"
EBCL_TF_IMAGE_BASE="${WORKSPACE}/downloaded_images/"
echo ${EBCL_TF_IMAGE_BASE}
export EBCL_TF_IMAGE_BASE
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
export EBCL_IMAGE_BASE_ARTIFACTORY
EBCL_IMAGE_BUNDLE_PATH="${EBCL_TC_IMAGE}"
export EBCL_IMAGE_BUNDLE_PATH
EBCL_IMAGE_BUNDLE_NAME="build.tar.xz"
export EBCL_IMAGE_BUNDLE_NAME
EBCL_IMAGE_BUNDLE_URL="${EBCL_IMAGE_BASE_ARTIFACTORY}/${EBCL_IMAGE_BUNDLE_PATH}/${EBCL_IMAGE_BUNDLE_NAME}"
export EBCL_IMAGE_BUNDLE_URL


# QEMU COMMAND
EBCL_TC_QEMU_NETWORK_APPEND="ipv6-net=fd00::eb/64,\
ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3,\
net=192.168.7.0/24,dhcpstart=192.168.7.50,\
host=192.168.7.1,dns=192.168.7.3"
export EBCL_TC_QEMU_NETWORK_APPEND
EBCL_TC_QEMU_KERNEL_CMDLINE=""
export EBCL_TC_QEMU_KERNEL_CMDLINE
EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND=""
export EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND

# Test Image
if [[ "${EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND}" == *"verity"* ]]; then
    : "${EBCL_ROOT_IMAGE_FILE_NAME:=image.verity.raw}"
else
    : "${EBCL_ROOT_IMAGE_FILE_NAME:=image.raw}"
fi

: "${EBCL_KERNEL_FILE_NAME:=vmlinuz}"
: "${EBCL_INITRD_FILE_NAME:=initrd.img}"

: "${EBCL_STORAGE_DIRECTORY:=${EBCL_TF_IMAGE_BASE}/${EBCL_IMAGE_BUNDLE_PATH}}/"
export EBCL_STORAGE_DIRECTORY
: "${EBCL_ROOT_IMAGE:=${EBCL_TF_IMAGE_BASE}/${EBCL_IMAGE_BUNDLE_PATH}/${EBCL_ROOT_IMAGE_FILE_NAME}}"
: "${EBCL_KERNEL:=${EBCL_TF_IMAGE_BASE}/${EBCL_IMAGE_BUNDLE_PATH}/${EBCL_KERNEL_FILE_NAME}}"
: "${EBCL_INITRD:=${EBCL_TF_IMAGE_BASE}/${EBCL_IMAGE_BUNDLE_PATH}/${EBCL_INITRD_FILE_NAME}}"

# tests run by default
TEST_SUITE="ebcl_base"
export TEST_SUITE

EBCL_QEMU_CMDLINE_AARCH64="qemu-system-aarch64 \
        -machine virt -cpu cortex-a72 -machine type=virt -nographic -m 4G \
        -netdev user,id=mynet0${EBCL_TC_QEMU_NETWORK_APPEND} \
        -device virtio-net-pci,netdev=mynet0 \
        -kernel "${EBCL_KERNEL}" \
        -append ${EBCL_TC_QEMU_KERNEL_CMDLINE} ${EBCL_TC_QEMU_KERNEL_CMDLINE_APPEND} \
        -initrd ${EBCL_INITRD} \
        -drive format=raw,file=${EBCL_ROOT_IMAGE},if=virtio}"

EBCL_QEMU_CMDLINE="${EBCL_QEMU_CMDLINE_AARCH64}"
export EBCL_QEMU_CMDLINE
echo "EBCL_QEMU_CMDLINE: ${EBCL_QEMU_CMDLINE}"

#TEST_SUITE="crinit.robot"
#export TEST_SUITE

# todo EBCL_TF_CLEAR_CMD="task mrproper"

# EBCL_TC_IMAGE
# EBCL_TC_SHUTDOWN_COMMAND
# EBCL_TC_SHUTDOWN_TARGET
