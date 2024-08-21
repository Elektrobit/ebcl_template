# The amd64 images

EB corbos Linux doesn’t support any amd64 hardware at the moment, but we provide some QEMU amd64 images. Using amd64 for development may help to make your development flow much smoother since you don’t have to handle the tricky aspects of cross-building.

For _amd64/qemu_ we provide example images for EB corbos Linux (EBcL) and for Ubuntu Jammy. The difference between EBcl and Jammy is, that EBcL provides some additional components, like the _crinit_ init-manager and the _elos_ logging and event framework, and that EBcL provides a qualified security maintenance release every three months, while Jammy is proving updates continuously, using less strict qualification and documentation.

## The amd64 Jammy images

In _images/amd64/qemu/jammy_ you can find five basic example images demonstrating how to use the EB corbos Linux SDK. This folder contains the common configuration shared by all the examples, and makes use of the QEMU _images/qemu*.mk_ include makefiles.

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
arch: 'amd64'
```

All examples make use of the kernel “linux-image-generic”. This is a meta-package and always takes the latest available Ubuntu Jammy package. The Canonical Ubuntu apt repositories are used to build the examples.

```yaml
# Partition layout of the image
# For more details see https://elektrobit.github.io/embdgen/index.html
image:
  type: gpt
  boot_partition: root

  parts:
    - name: root
      type: partition
      fstype: ext4
      size: 2 GB
      content:
        type: ext4
        content:
          type: archive
          archive: build/ubuntu.config.tar
```

All examples make use of a very simple image consisting of a gpt partition table and a single ext4 root partition with a size of 2 GB.

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Root device to mount
root_device: /dev/vda1
# List of kernel modules
modules:
  - kernel/drivers/block/virtio_blk.ko # virtio_blk is needed for QEMU
```

Also the _initrd.img_ is shared by all examples. It first loads the virt-IO block driver and then mounts _/dev/vda1_ as the root filesystem.

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Download dependencies of the kernel package - necessary if meta-package is specified
download_deps: true
# Files to copy from the packages
files:
  - boot/vmlinuz*
  - boot/config*
# Do not pack the files as tar - we need to provide the kernel binary to QEMU
tar: false
```

The _boot.yaml_ is also not image specific. It’s used to download and extract the kernel binary. In addition, the kernel config is extracted.

```yaml
# Derive the base configuration
base: base.yaml
# Reset the kernel - should not be installed
kernel: null
# Name of the archive.
name: ubuntu
# Packages to install in the root tarball
packages:
  - systemd
  - udev        # udev will create the device node for ttyS0
  - util-linux
# Scripts to configure the root tarball
scripts:
  - name: config_root.sh # Name of the script, relative path to this file
    env: chroot # Type of execution environment - chfake means fakechroot
```

The _root.yaml_ shares the common parts of the root filesystem configuration of all these example images. All examples use “ubuntu” as name, by default have a minimal root filesystem only consisting of _debootstrap_ and _systemd_, _udev_, and _util-linux_ additionally installed, and use the _config_root.sh_ as configuration, which links _systemd_ as _/sbin/init_.

## The amd64 Jammy berrymill image

At the moment, the EBcL SDK makes use of two more generic Linux root filesystem builders, _elbe_ and _kiwi-ng_. The default is _elbe_, because it provides a much better build speed, but also the previously used _kiwi-ng_ is still supported. Future EBcL major release lines may drop both and come with a more embedded optimized solution, so ideally you make use of the _root.yaml_ instead of using an own elbe or kiwi-ng XML image description.

The _amd64/qemu/jammy/berrymill_ image makes use of the above mentioned configurations, and extends it with an own _root.yaml_ and a specific _Makefile_.

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
# Makefile for ammy QEMU amd64 image using kiwi

# Arch for sysroot extraction
arch = x86_64

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
include ../../../../qemu_x86_64.mk
```

The _Makefile_ point _make_ to the right specification files, sets the flag to mount the root filesystem as writable, and includes the base makefiles describing how to build an QEMU image and how to run the build results using QEMU.

## The amd64 Jammy debootstrap image

In general, _kiwi-ng_ can also build images using debootstrap instead of a pre-built bootstrap package. This brings the limitation that only one apt repository is supported, which needs to provide a proper main component, and that a _debootstrap_ script must be available in the build VM for the selected distribution. The EBcL SDK can make use of this for Ubuntu Jammy builds, and the image _amd64/qemu/jammy/debootstrap_ is a proof of concept showing how to do it.

```yaml
# CPU architecture
arch: amd64
# Name of tarball
name: ubuntu
# APT repo for kiwi build
apt_repos:
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy
    components:
      - main
      - universe
# Use debootstrap instead of bootstrap package
# This allows us to use only one apt repo.
use_bootstrap_package: false
# Select required bootstrap packages
bootstrap:
  - apt
# Packages to install in the root tarball
packages:
  - systemd
  - udev
  - util-linux
# Overwrite the image builder type - ensure kiwi is used
type: kiwi
# Pattern to match the result file
result_pattern: '*.tar.xz'
# Scripts to configure the root tarball
scripts:
  - name: ../config_root.sh # Name of the script, relative path to this file
    env: chroot # Type of execution environment
```

The _root.yaml_ configures the Ubuntu Jammy apt repository as the single apt repository to use, and sets the “use_bootstrap_package” to false, which will result in a kiwi-ng build not relying on the EBcL bootstrap package.

## The amd64 Jammy elbe image

The _images/amd64/qemu/jammy/elbe_ image makes use of the _elbe_ root filesystem builder. The only difference to the shared configuration is that _elbe_ is explicitly selected.

```yaml
# Config to use as a base
base: ../root.yaml
# Overwrite the image builder type - ensure elbe is used
type: elbe
```
The _Makefile_ is similar to the one above.

## The amd64 Jammy kernel source

The _amd64/qemu/jammy/kernel_src_ image is a proof of concept showing how to make use of local compiled kernels with EBcL builds. The _boot.yaml_ is used to 





