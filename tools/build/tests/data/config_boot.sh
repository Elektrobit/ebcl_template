#!/bin/sh

echo "Temporary boot folder is $1"

mkdir -p $1/boot
touch $1/boot/some_config
