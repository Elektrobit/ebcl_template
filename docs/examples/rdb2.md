# EB corbos Linux example images for the NXP RDB2 board

The folder_images/arm64/nxp/rdb2_ contains the EB corbos Linux (EBcL) example images for the NXP RDB2 development board, which is equipped with an NXP S32G2 SoC.
The S32G2 has very specific storage layout requirements, and if you are interested into more details about required base configuration, take a look at [Building an image from scratch](../images/from_scatch.md).

```yaml
# Kernel package to use
kernel: linux-image-unsigned-5.15.0-1034-s32-eb
# CPU architecture
arch: arm64
# Add the EB corbos Linux apt repo
use_ebcl_apt: true
# Add repo with NXP RDB2 packages
apt_repos:
  - apt_repo: http://linux.elektrobit.com/eb-corbos-linux/1.2
    distro: ebcl_nxp_public
    components:
      - nxp_public
    key: file:///build/keys/elektrobit.pub
    gpg: /etc/berrymill/keyrings.d/elektrobit.gpg
```

The packages for the NXP RDB2 board are provided as a separate distribution, called _ebcl_nxp_public_, as component _nxp_public_. For the RDB2 images, the kernel package _linux-image-unsigned-5.15.0-1034-s32-eb_ is used.
This package contains a Linux kernel image for the S32G2, and has slightly different kernel  configuration as the Ubuntu Jammy default.


The _image.yaml_ describes the required storage layout, the _initrd.yaml_ is a very minimal _initrd.img_ specification, just defining the root partition.
The _boot_root.yaml_ defines the environment used for building the _fitimage_. The _bootargs*_ files are the S32G2 specific configurations for the _fitimage_ layout and kernel command line.
The script _build_fitimage.sh_ is executed in the mentioned chroot environment, and automates the fitimage building.
The _boot.yaml_ wraps all the before mentioned, and is used together with the _boot generator_ to automatically build the fitimage.
The _rdb2.mk_ defines the default build flow for the RDB2 images, and is included and extended if needed by the makefiles of the different image variants.

## EBcL RDB2 systemd image

The minimal RDB2 _systemd_ example image is contained in the folder _images/arm64/nxp/rdb2/systemd_. This image defines a minimal working RDB2 image, and provides only _systemd_, _udev_ and _util-linux_ in the userland.

## EBcL RDB2 systemd server image

The folder _images/arm64/nxp/rdb2/systemd/server_ contains a Raspberry Pi server like image for the RDB2 board.
This image comes with and SSH server, apt, and mtd-utils.

## EBcL RDB2 crinit image

The minimal RDB2 _crinit_ example image is contained in the folder _images/arm64/nxp/rdb2/crinit_. This image defines a minimal working RDB2 image, and provides only _crinit_ in the userland.

## EBcL RDB2 network image

The RDB2 network example image is contained in the folder _images/arm64/nxp/rdb2/network_. This image contains _crinit_, _elos_, and _netifd_ to provide a minimal Linux image with network support and logging.
This image also shows how to use the _boot generator_ and the _root generator_ to add modules to a root filesystem.
The _boot.yaml_ defines that the _lib/modules_ folder shall be extracted to the build results folder, and the _root.yaml_ picks this result up and includes it into the root filesystem using the following yaml lines:

```yaml
host_files:
  - source: $$RESULTS$$/modules
    destination: lib
```

The _crinit_config_ folder contains a small implementation to make use of these modules.
The crinit task _crinit_config/etc/crinit/crinit.d/modprobe.crinit_ runs the script _crinit_config/usr/sbin/load_modules.sh_ which loads all modules state in _crinit_config/etc/kernel/runtime_modules.conf_. This is a bit more involved, and requires more knowledge about the used hardware, as using _udev_ would need, but it is also much more lightweight and faster than _udev_.

## EBcL RDB2 kernel_src image

The folder _images/arm64/nxp/rdb2/kernel_src_ contains a proof of concept on how to use a locally built kernel for an RDB2 image.
The _kernel_config.yaml_ is used to extract the default kernel config, the _Taskfile_ downloads and builds the kernel, and the _boot.yaml_ picks the kernel binary up and adds it to the _fitimage.
More details are described in the chapter [Kernel development](../kernel.md).
