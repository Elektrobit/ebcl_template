# EB corbos Linux workspace template

This repository contains a VS Code workspace template for EB corbos Linux application and image development.

## Content

The workspace is structured in the following way:

- _.devcontainer_: VS Code devcontainer configuration files
- _.vscode_: VS Code configuration files
- _apps_: applications and config packages
    - _my-config_: config package example
    - _my-json-app_: user app packaging example
- _apt_: workspace specific apt repository
- _bin_: workspace specific scripts and binaries
- _gpg-keys_: workspace keys for repository signing
    - _env.sh_: user identity for Debian packaging
- _images_: example image descriptions
    - _qemu-crinit-aarch64_: QEMU example image for Arm aarch64 CPU architecture using crinit init manager
    - _qemu-crinit-x86_64_: QEMU example image for Intel x86_64 CPU architecture using crinit init manager
    - _qemu-systemd-aarch64_: QEMU example image for Arm aarch64 CPU architecture using systemd init manager
    - _qemu-systemd-x86_64_: QEMU example image for Intel x86_64 CPU architecture using systemd init manager
    - _raspberry-pi-crinit_: Raspberry Pi 4 image using crinit init manager
    - _raspberry-pi-systemd_: Raspberry Pi 4 image using systemd init manager
    - _rdb2-crinit_: RDB2 image using crinit init manager
    - _rdb2_systemd_: RDB2 image using systemd init manager
- _result_: build results
    - _app_: app build and packaging results
    - _image_: image build results
- _sysroot_aarch64_: sysroot for cross-compiling for Arm aarch64 CPU architecture
- _sysroot_x86_64_: sysroot for cross-compiling for Intel x86_64 CPU architecture

## Usage

The workspace can be used with a VS Code setup with dev containers support.
For details how to setup this environment, please take a look at https://code.visualstudio.com/docs/devcontainers/containers.

To prepare the sysroots, build the app, and build the images, you can make use of the provided tasks in `.vscode/tasks.json`.
These tasks are considered as a template for your own use case specific tasks.
To run a task, press "CTRL" + "SHIFT" + "B". This will bring up a menu showing all the available tasks.

This workspace provides the following example tasks:

- _EBcL: Image Raspberry Pi crinit_: Build the Rasperry Pi crinit image.
- _EBcL: Image Raspberry Pi systemd_: Build the Rasperry Pi systemd image.
- _EBcL: Image qemu-crinit (aarch64)_: Build the aarch64 QEMU crinit image.
- _EBcL: Image qemu-crinit (x86_64)_: Build the x86_64 QEMU crinit image.
- _EBcL: Image qemu-systemd (aarch64)_: Build the aarch64 QEMU systemd image.
- _EBcL: Image qemu-systemd (x86_64)_: Build the x86_64 QEMU systemd image.
- _EBcL: Image rdb2-systemd_: Prepare sysroot RDB2 systemd image.
- _EBcL: Image rdb2-crinit_: Prepare sysroot RDB2 crinit image.
- _EBcL: Run QEMU crinit (aarch64)_: Run the QEMU crinit aarch64 image.
- _EBcL: Run QEMU crinit (x86_64)_: Run the QEMU crinit x86_64 image.
- _EBcL: Run QEMU systemd (aarch64)_: Run the QEMU systemd aarch64 image.
- _EBcL: Run QEMU systemd (x86_64)_: Run the QEMU systemd x86_64 image.
- _EBcL: Sysroot Raspberry Pi crinit_: Prepare sysroot aarch64 for the Rasperry Pi crinit image.
- _EBcL: Sysroot Raspberry Pi systemd_: Prepare sysroot aarch64 for the Rasperry Pi systemd image.
- _EBcL: Sysroot qemu-crinit (aarch64)_: Prepare sysroot aarch64 QEMU crinit image.
- _EBcL: Sysroot qemu-crinit (x86_64)_: Prepare sysroot x86_64 QEMU crinit image.
- _EBcL: Sysroot qemu-systemd (aarch64)_: Prepare sysroot aarch64 QEMU systemd image.
- _EBcL: Sysroot qemu-systemd (x86_64)_: Prepare sysroot x86_64 QEMU systemd image.
- _EBcL: Sysroot rdb2-systemd_: Prepare sysroot RDB2 systemd image.
- _EBcL: Sysroot rdb2-crinit_: Prepare sysroot RDB2 crinit image.
- _EBcL: App (aarch64)_: Build CMake App for aarch64.
- _EBcL: App (x86_64)_: Build CMake App for x86_64.
- _EBcL: Generate signing key_: Generate a signing key for Debian packageing. Please update gpg-keys/env.sh before running this task!
- _EBcL: Generate Debian metadata for app_: Generate the Debian metadata for the app. Please update gpg-keys/env.sh before running this task!
- _EBcL: Generate Debian metadata for config_: Generate the Debian metadata for the app. Please update gpg-keys/env.sh before running this task!
- _EBcL: Package app (x86_64)_: Generate the x86_64 Debian package of the app. Debian metadata and the sysroot must be avaiable!
- _EBcL: Package app (aarch64)_: Generate the aarch64 Debian package of the app. Debian metadata and the sysroot must be avaiable!
- _EBcL: Prepare local repository_: Generate apt repositry metadata and Berrymill config for generated Debian packages.
- _EBcL: Serve app packages_: Serve the apt repository containg the generated Debian packages.
- _EBcL: Serve workspace apt folder_: Serve the apt repository containg the generated Debian packages.
- _EBcL: Build config package_: Build a platform indepent Makefile package.

The used EB corbos Linux SDK container provides the following commands:


Commands for image building:

- _cross_build_image.sh_ "path to image description folder": build an aarch64 image description
- _box_build_image.sh_ "path to image description folder": build an x86_64 image description
- _kvm_build_image.sh_ "path to image description folder": build an x86_64 image description using KVM acceleration.
  To use this command, the host must support KVM virtualization, and the container must be executed in _privileged_
  mode (see _.devcontainer/devcontainer.json_).

Commands for image testing:

- _qemu_efi_aarch64.sh_ "path to disk image": runs a QEMU VM using the given Arm aarch64 disk image
  This command expects that the image supports EFI boot.
- _qemu_efi_x86_64.sh_ "path to disk image": runs a QEMU VM using the given Intel x86_64 disk image
  This command expects that the image supports EFI boot.

Commands for sysroot preparation:

- _cross_build_sysroot.sh_ "path to image description folder": prepares an aarch64 sysroot for the given image description
  Please clear the Arm aarch64 sysroot folder _sysroot_aarch64_ before running this command.
- _box_build_sysroot.sh_ "path to image description folder": prepares an x86_64 sysroot for the given image description
  Please clear the Intel x86_64 sysroot folder _sysroot_x86_64_ before running this command.

Commands for app compilation:

- _cmake_aarch64.sh_ "path to app source folder": cross-compile the given cmake app for the image used to prepare the _sysroot_aarch64_
- _cmake_x86_64.sh_ "path to app source folder":  compile the given cmake app for the image used to prepare the _sysroot_x86_64_ 

Commands for Debian packaging:

- _prepare_deb_metadata.sh_ "path to app source folder" "package name" "package version": initally generate the Debian package metadata for the given app or config package
  Please update gpg-keys/env.sh before running this task!
  The generated metadata should be manually completed, and versioned in parallel to the app source code.
- _cross_build_package.sh_ "path to app source folder": cross-build an aarch64/arm64 Debian package of the given app
  Before using this command, the Debian metadata must be available and updated.
- _build_package.sh_ "path to app source folder": build an x86_64/amd64 Debian package of the given app
  Before using this command, the Debian metadata must be available and updated.
- _build_config_package.sh_ "path to config source folder": build a Debian package containing the config files for aarch64/arm64 and x86_64/amd64.
  Before using this command, the Debian metadata must be available and updated.

Commands for local apt repository:

- _gen_sign_key.sh_: generate a GPG key later used for Debian repository metadata signing.
  Please update your data in _gpg-keys/env.sh_ before running this command.
  This script updates environment variables. Please run it as `source gen_sign_key.sh` to apply the
  changes to the current shell.
- _prepare_repo_config.sh_: generate apt repository metadata, signed with the available primary GPG key
  This command generates valid apt repository metadata for all Debian packages found in the _result/app_
  workspace folder. It also generates a Berrymill config template and config file containing the current
  contianer IP address and the local repository. This allows to use these local packages in local image
  builds when the repository server was started.
- _serve_packages.sh_ "path to apt repository": run a server for a local apt repository
  - use path _result/app_ to use locally created packages form this folder
  - use path _apt_ to serve a workspace specific apt repository contained in the _apt_ folder
