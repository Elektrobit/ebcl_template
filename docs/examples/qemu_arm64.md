# The arm64 images

EB corbos Linux comes with arm64 baesedxample images for rpi4 and nxp s32g boards at the moment.
To ease development and testing we also provide QEMU arm64 images.

For _arm64/qemu_ we provide example images for EB corbos Linux (EBcL) and for Ubuntu Jammy.
The difference between EBcl and Jammy is, that EBcL provides some additional components, like the _crinit_ init-manager and the _elos_ logging and event framework, and that EBcL provides a qualified security maintenance release every three months, while Jammy is proving updates continuously, using less strict qualification and documentation.

## The arm64 Jammy images

In _images/arm64/qemu/jammy_ you can find two basic example images demonstrating how to use the EB corbos Linux SDK.
This folder contains the common configuration shared by all the examples, and makes use of the QEMU _images/qemu*.mk_ include makefiles.

```yaml
# Kernel package to use
kernel: linux-image-generic
# Apt repositories to use
apt_repos:
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy
    components:
      - main
      - universe
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy-security
    components:
      - main
      - universe
# CPU architecture
arch: 'arm64'
```

All examples make use of the kernel “linux-image-generic”. This is a meta-package and always takes the latest available Ubuntu Jammy package.
The Canonical Ubuntu apt repositories are used to build the examples.

Note that the only difference to the corresponding amd64 image is the arch specification in the last line, all further shared yaml files for the arm64 Jammy images with berrymill and elbe are identical to the amd64 QEMU jammy images, and hence documented already in the previous section.

## The arm4 Jammy images

At the moment, the EBcL SDK makes use of two more generic Linux root filesystem builders, _elbe_ and _kiwi-ng_. The default is _elbe_, because it provides a much better build speed, but also the previously used _kiwi-ng_ is still supported.
Note that _kiwi-ng_ is wrapped by _berrymill_ to provide additional features like derived images.
Future EBcL major release lines may drop both and come with a more embedded optimized solution, so ideally you make use of the _root.yaml_ instead of using an own elbe or kiwi-ng XML image description.

The _arm64/qemu/jammy/berrymill_ image makes use of the above mentioned configurations, and extends it with an own _root.yaml_ and a specific _Makefile_.

```yaml
# Config to use as a base
base: ../root.yaml
# Add the EB corbos Linux apt repo to provide the boostrap package
use_ebcl_apt: true
# Overwrite the image builder type - ensure kiwi is used
type: kiwi
# Pattern to match the result file
result_pattern: '*.tar.xz'
```

This _root.yaml_ inherits the _root.yaml_ from the partent folder, described above, and adds the EBcL apt repository, which provides the required kiwi-ng bootstrap package, set the build type to “kiwi” and updates the build result search pattern to “*.tar.xz”, since there is no way to disable the result compression with _kiwi-ng_.

```make
# Makefile for any QEMU arm64 image using kiwi

# Arch for sysroot extraction
arch = aarch64

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec = root.yaml
# Specification of the initrd.img
initrd_spec = ../initrd.yaml
# Specification of the kernel
boot_spec = ../boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = ../config_root.sh


#--------------------
# Generated artifacts
#--------------------

# Disc image
disc_image = $(result_folder)/image.raw

# Base root tarball
base_tarball = $(result_folder)/ubuntu.tar.xz

# Configured root tarball
root_tarball = $(result_folder)/ubuntu.config.tar

# Generated initrd.img
initrd_img = $(result_folder)/initrd.img

# Kernel image
kernel = $(result_folder)/vmlinuz

# Sysroot tarball
sysroot_tarball = $(result_folder)/ubuntu_sysroot.tar


#-------------------
# Run the QEMU image
#-------------------

# QEMU kernel command line
kernel_cmdline_append = "rw"


# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_aarch64.mk
```

The _Makefile_ point _make_ to the right specification files, sets the flag to mount the root filesystem as writable, and includes the base makefiles describing how to build an QEMU image and how to run the build results using QEMU.

## The arm64 EB corbos Linux images

EB corbos Linux (EBcL) is an embedded Linux distribution targeting automotive and other industrial embedded Linux solutions.
The main differences between EBcL and Ubuntu are the release and qualification handling, and some additional components added by EBcL which allow building more lightweight and better performing embedded images.
The code is again very similar to the amd64 QEMU images.

The differences for aarch64 are the adaption of the architecture in _base.yaml_ and in _*.mk_ files.

### Supported images

The following images are supported:

- aarch64 EB corbos Linux systemd berrymill
- aarch64 EB corbos Linux systemd elbe image
- aarch64 EB corbos Linux crinit images 
- aarch64 EB corbos Linux crinit berrymill image

Their functuonality and implementation is analog to the corresponding amd64 images.
