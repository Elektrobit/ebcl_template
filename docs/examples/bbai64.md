# EB corbos Linux example images for the Beaglebone AI 64

The Beaglebone AI 64 example images make use of the kernel and firmware packages provided by [Beaglebone Repo](http://debian.beagleboard.org/arm64), as well as [Ubuntu Ports](http://ports.ubuntu.com/ubuntu-ports/)for general packages and security fixes.

```yaml
# CPU architecture
arch: arm64
apt_repos:
  - apt_repo: http://ports.ubuntu.com/ubuntu-ports
    distro: jammy
    components:
      - main
      - universe
      - multiverse
      - restricted
  # Get latest security fixes
  - apt_repo: http://ports.ubuntu.com/ubuntu-ports
    distro: jammy-security
    components:
      - main
      - universe
      - multiverse
      - restricted
  # Get Kernel Package and Firmware
  - apt_repo: http://debian.beagleboard.org/arm64
    gpg: /tmp/bbbio.gpg
    distro: jammy
    components:
      - main
use_ebcl_apt: true
```

For booting, the Beaglebone AI 64 expects to find a fat32 partition as first partition on the SD card, and this partition is expected to contain the firmware and kernel binaries and devicetrees, and some configuration files.
For this image, we make use of the split archive feature of _embdgen_. This feature allows the distribution of the content of one tarball to multiple partitions.
The following _image.yaml_ gets the content of _build/boot.tar_, and puts the content to the _boot_ partition. The second partition contains the root filesystem and is populated from the _build/root.config.tar_ archive

```yaml
# Partition layout of the image
# For more details see https://elektrobit.github.io/embdgen/index.html
image:
  type: mbr
  boot_partition: boot
  parts:          
    - name: boot
      type: partition
      start: 2048 B
      fstype: fat32
      content:
        type: fat32
        content:
          type: archive
          archive: build/boot.tar
      size: 256 MB

    - name: root
      type: partition
      fstype: ext4
      size: 2 GB
      content:
        type: ext4
        content:
          type: archive
          archive: build/root.config.tar

```

The content of the boot partition is created with the help of the boot_root.yaml description. Here packages that contain important files for the boot partition, like firmware, dtb and uboot binaries are installed. Following this, some files will get prepared for extraction in the boot_configure.sh script and finally extracted as described in the boot_extract.yaml

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Reset the kernel value - we don't want to download and extract it
kernel: null
# Do pack the files as tar
tar: true
# do not download and extract these packages, they are already installed in the tools.tar
use_packages: false
# Name of the boot root archive
base_tarball: $$RESULTS$$/boot_root.tar
host_files:
  - source: $$RESULTS$$/initrd.img 
files:
  - opt/u-boot/bb-u-boot-beagleboneai64/sysfw.itb
  - opt/u-boot/bb-u-boot-beagleboneai64/tiboot3.bin
  - opt/u-boot/bb-u-boot-beagleboneai64/tispl.bin
  - opt/u-boot/bb-u-boot-beagleboneai64/u-boot.img
  - initrd.img
  - outdir/*

scripts:
  - name: boot_configure.sh

```
## EBcL Beaglebone AI 64 systemd image

The folder _images/arm64/beaglebone/ai64/systemd_ contains the _systemd_ variant of the Beaglebone AI 64 image.
This image is not a minimal one, but brings what you expect to find in a Beaglebone AI 64 server image.
Since we use the split archive feature, we install also the kernel and bootloader package to the root filesystem, which feels a bit simpler and we don’t need to care about the needed kernel modules, but also give a bit more bloated and less secure root filesystem.

```yaml
base: ../base.yaml
# reset the kernel value
kernel: bbb.io-kernel-5.10-ti-k3-j721e
# Packages to install in the root tarball
packages:
  - kmod # requried to load modules
  - systemd
  - systemd-timesyncd
  - systemd-coredump
  - udev
  - dbus
  # network helpers
  - iproute2
  - iputils-ping
  # SSH server
  - openssh-server
  # Other basic tools
  - openssh-client
  - bash
  - apt 
  - ca-certificates
  - util-linux
  - cron
  - file
  - findutils
  - iproute2
  - iptables
  - iputils-ping
  - gnupg
  # Editors
  - vim
  - python3
  - bb-j721e-evm-firmware
# Scripts to configure the root tarball
host_files:
  - source: system_config/*
    uid: 0
    gid: 0
    mode: 755
scripts:
  - name: config_root.sh # Name of the script, relative path to this file
    env: chroot # Type of execution environment
```

The _config_root.sh_ links _systemd_ as init-manager and enables the basic system services for network, NTP and DNS.
The _system_config_ overlay folder provides a basic system configuration, including apt and SSH.

## EBcL Beaglebone AI 64 crinit image

The _crinit_ variant of the Beaglebone AI 64 image, contained in _images/arm64/beaglebone/ai64/crinit_, makes use of the _crinit_ init-manager, _elos_ for logging, and _netifd_ for the network configuration.
It also comes with apt and SSH support, and provides typical tools like _vim_ or _strace_. The script _config_root.sh_ takes care of creating the machine ID, needed by _elos_, and makes sure DNS is working.
All other configuration is provided as an overlay in the _system_config_ folder.
