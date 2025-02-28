# EB corbos Linux example images for the NXP RDB2 board

The folder_images/arm64/nxp/rdb2_ contains the EB corbos Linux (EBcL) example images for the NXP RDB2 development board, which is equipped with an NXP S32G SoC.
The S32G has very specific storage layout requirements, and if you are interested into more details about required base configuration, take a look at [Building an image from scratch](../images/from_scatch.md).

```yaml
# Kernel package to use
kernel: linux-image-unsigned-5.15.0-1041-s32-eb
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

The packages for the NXP RDB2 board are provided as a separate distribution, called _ebcl_nxp_public_, as component _nxp_public_. For the RDB2 images, the kernel package _linux-image-unsigned-5.15.0-1041-s32-eb_ is used.
This package contains a Linux kernel image for the S32G2, and has slightly different kernel configuration than the Ubuntu Jammy default.

Please be aware that the firmware for different peripherals, like the LLCE and the PFE, is proprietary
and we are not allow to distribute it publicly, so if you build an image using the public EB corbos Linux repository,
you will not be able to make use of the CAN ports attached to the LLCE, or the network ports attached to the PFE.
If you are a paying customer, and have signed the NXP redistribution agreement, you will get access to _ebcl_nxp_,
which is identical to _ebcl_nxp_public_, except the fact that it also provides these proprietary firmware.

The _image.yaml_ describes the required storage layout, the _initrd.yaml_ is a very minimal _initrd.img_ specification,
just defining the root partition.
The _boot_root.yaml_ defines the environment used for building the _fitimage_. The _bootargs*_ files,
contained in _images/common/nxp/rdb2_, are the S32G2 specific configurations for the _fitimage_ layout and kernel command line.
The script _images/common/nxp/rdb2/build_fitimage.sh_ is executed in the mentioned chroot environment,
and automates the fitimage building.
The _boot.yaml_ wraps all the before mentioned, and is used together with the _boot generator_ to automatically build the fitimage.

The build flow for all NXP RDB2 images is specified in _images/tasks/RDB2_image.yml_,
included by the _Taskfile.yml_ of the different image descriptions,
and described in detail in [Building an image from scratch](../images/from_scatch.md).

## EBcL 1.x RDB2 crinit image

The EBcL 1.x RDB2 crinit image is contained in the folder _images/arm64/nxp/rdb2/ebcl_1.x_crinit_.
This image contains _crinit_, _elos_, and _netifd_ to provides a Linux image for interactive exploration.

The _crinit_config_ folder contains a small implementation to load kernel modules using the crinit init manager.
The crinit task _images/common/nxp/rdb2/crinit/config/etc/crinit/crinit.d/modprobe.crinit_
runs the script _images/common/nxp/rdb2/crinit/config/usr/sbin/load_modules.sh_
which loads all modules state in _images/common/nxp/rdb2/crinit/config/etc/kernel/runtime_modules.conf_.
This is a bit more involved, and requires more knowledge about the used hardware, as using _udev_ would need,
but it is also much more lightweight and faster than _udev_.

## EBcL 1.x RDB2 systemd image

The EBcL 1.x RDB2 systemd image description is contained in _images/arm64/nxp/rdb2/ebcl_1.x_systemd_.
It's quite similar to the EBcL 1.x RDB2 crinit image, but makes use of _systemd_ and _udev_.
