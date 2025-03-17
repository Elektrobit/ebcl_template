#!/bin/bash

echo "${EBCL_TC_QEMU_BIN} ${EBCL_TC_QEMU_PARAMS} -m ${EBCL_TC_QEMU_MEMORY} \
        -netdev \"${EBCL_TC_QEMU_NETDEV}\" \
        -device \"${EBCL_TC_QEMU_DEVICE}\" \
        -kernel ${EBCL_TC_IMAGE_KERNEL} \
        -append \"${EBCL_TC_IMAGE_KERNEL_CMDLINE} ${EBCL_TC_IMAGE_KERNEL_CMDLINE_APPEND}\" \
        -initrd ${EBCL_TC_IMAGE_INITRD} \
        -drive \"format=raw,file=${EBCL_TC_IMAGE_DISC},if=virtio\"" \
        ${EBCL_TC_QEMU_ADDITIONAL_PARAMETERS} \
        >> qemu.log

${EBCL_TC_QEMU_BIN} ${EBCL_TC_QEMU_PARAMS} -m ${EBCL_TC_QEMU_MEMORY} \
        -netdev "${EBCL_TC_QEMU_NETDEV}" \
        -device "${EBCL_TC_QEMU_DEVICE}" \
        -kernel "${EBCL_TC_IMAGE_KERNEL}" \
        -append "${EBCL_TC_IMAGE_KERNEL_CMDLINE} ${EBCL_TC_IMAGE_KERNEL_CMDLINE_APPEND}" \
        -initrd "${EBCL_TC_IMAGE_INITRD}" \
        -drive "format=raw,file=${EBCL_TC_IMAGE_DISC},if=virtio" \
        ${EBCL_TC_QEMU_ADDITIONAL_PARAMETERS}
