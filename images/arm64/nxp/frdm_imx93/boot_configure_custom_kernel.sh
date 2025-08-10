#!/bin/sh
export KERNEL_VERSION=kernel_ver=$(cat "boot/utsrelease.h" | awk '{print $3}' | sed 's/\"//g' )
echo "Using kernel version: ${KERNEL_VERSION}"
