#!/bin/bash

sudo apt install zip

cp README.md build
cp run.sh build
cd build

zip -r qemu_image.zip README.md run.sh image.raw vmlinuz initrd.img
