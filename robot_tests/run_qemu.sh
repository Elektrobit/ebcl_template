#!/bin/bash

if [ -n "${EBCL_TC_QEMU_GUESS_CONFIG}" ]; then
        echo "Guessing QEMU parameters..."
        if [[ $EBCL_TC_IMAGE_DISC == *"arm64"* ]]; then
                echo "Using ARM64 QEMU parameters..."
                export EBCL_TC_IMAGE_KERNEL_CMDLINE="console=ttyAMA0 root=/dev/vda1"
                export EBCL_TC_QEMU_BIN="qemu-system-aarch64"
                export EBCL_TC_QEMU_PARAMS="-machine virt -cpu cortex-a72 -machine type=virt -nographic"
        else
                echo "Using AMD64 QEMU parameters..."
                export EBCL_TC_IMAGE_KERNEL_CMDLINE="console=ttyS0 root=/dev/vda1"
                export EBCL_TC_QEMU_BIN="qemu-system-x86_64"
                export EBCL_TC_QEMU_PARAMS=" -nographic "
        fi
fi

echo "\nQEMU command:"
echo "${EBCL_TC_QEMU_BIN} ${EBCL_TC_QEMU_PARAMS} -m ${EBCL_TC_QEMU_MEMORY} \
        -netdev \"${EBCL_TC_QEMU_NETDEV}\" \
        -device \"${EBCL_TC_QEMU_DEVICE}\" \
        -kernel ${EBCL_TC_IMAGE_KERNEL} \
        -append \"${EBCL_TC_IMAGE_KERNEL_CMDLINE}\" \
        -initrd ${EBCL_TC_IMAGE_INITRD} \
        -drive \"format=raw,file=${EBCL_TC_IMAGE_DISC},if=virtio\""

${EBCL_TC_QEMU_BIN} ${EBCL_TC_QEMU_PARAMS} -m ${EBCL_TC_QEMU_MEMORY} \
        -netdev "${EBCL_TC_QEMU_NETDEV}" \
        -device "${EBCL_TC_QEMU_DEVICE}" \
        -kernel "${EBCL_TC_IMAGE_KERNEL}" \
        -append "${EBCL_TC_IMAGE_KERNEL_CMDLINE}" \
        -initrd "${EBCL_TC_IMAGE_INITRD}" \
        -drive "format=raw,file=${EBCL_TC_IMAGE_DISC},if=virtio"
