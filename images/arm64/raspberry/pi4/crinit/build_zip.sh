#!/bin/bash

sudo apt install zip

cp README.md build

cd build

zip -r rpi4_image.zip README.md image.raw
