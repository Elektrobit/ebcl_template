# EB corbos Linux workspace template

This repository contains a VS Code workspace template for EB corbos Linux application and image development.

## Content

The workspace is structured in the following way:

- The folder `app` contains the source code of the C/C++ application which shall be compiled for an EB corbos Linux image.
- The folder `images` contains examples of EB corbos Linux images which are intended as a base for your images.
- The folder `result` will be used for build results.
- The folder `sysroot_aarch64` will contain the sysroot for cross-compiling the app for ARM aarch64 architecture.
- The folder `sysroot_amd64` will contain the sysroot for compiling the app for x86_64/amd64 architecture.

## Usage

The workspace can be used with a VS Code setup with dev containers support. For details how to setup this environment, please take a look at https://code.visualstudio.com/docs/devcontainers/containers.

To prepare the sysroots, build the app, and build the images, you can make use of the provided tasks. Feel free to extend this tasks.

The used EB corbos Linux SDK container provides the following commands:

- Commands to prepare a sysroot:
  - `box_build_sysroot.sh <relative path to appliance XML>`: Prepare a sysroot for x86_64/amd64 for the given image.
  - `cross_build_sysroot.sh <relative path to appliance XML>`: Prepare a sysroot for aarch64/arm64 for the given image.
- Commands to build the application:
  - `cmake_amd64.sh`: Use cmake to build app for an amd64/x86_64 environment making use of `sysroot_amd64`.
  - `cmake_aarch64.sh`: Use cmake to build app for an aarch64/arm64 environment making use of `sysroot_aarch64`.
- Commands to build images:
  - `box_build_image.sh`: Build an image for and amd64/x86_64 SoC or QEMU.
  - `cross_build_image.sh`: Build an image for and aarch64/arm64 SoC or QEMU.
