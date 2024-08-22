# EB corbos Linux example images for the Raspberry Pi 4

EB corbos Linux comes with development support for the Raspberry Pi 4. This means, you can use a Raspberry Pi 4 board for early development and demos, and you get support, but it's not qualified for mass production. The Raspberry Pi 4 example images make use of the kernel and firmware packages provided by [Ubuntu Ports](http://ports.ubuntu.com/ubuntu-ports/).

```yaml
# Kernel package to use
kernel: linux-image-raspi
use_ebcl_apt: true
# Additional apt repos
apt_repos:
  # Get Ubuntu Raspberry Pi packages
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
# CPU architecture
arch: arm64
```

For booting, the Raspberry Pi expects to find a fat32 partition as first partition on the SD card, and this partition is expected to contain the firmware and kernel binaries and devicetrees, and some configuration files. For this image, we make use of the split archive feature of _embdgen_. This feature allows the distribution of the content of one tarball to multiple partitions. The following _image.yaml_ gets the content of _build/ebcl_pi4.config.tar_, and puts the content of the _/boot_ folder to the _boot_ partition and puts the remaining content to the _root_ partition.

```yaml
# Partition layout of the image
# For more details see https://elektrobit.github.io/embdgen/index.html
contents:
  - name: archive
    type: split_archive
    archive: build/ebcl_pi4.config.tar
    splits:
      - name: boot
        root: boot
    remaining: root

image:
  type: mbr
  boot_partition: boot

  parts:
    - name: boot
      type: partition
      fstype: fat32
      size: 200 MB
      content:
        type: fat32
        content: archive.boot

    - name: root
      type: partition
      fstype: ext4
      size: 4 GB
      content:
        type: ext4
        content: archive.root
```

The _commandline.txt_ and _config.txt_ are just taken from a prebuilt Raspberry Pi OS image. 

```bash
#!/bin/sh

# Create a hostname file
echo "ebcl-pi4" > ./etc/hostname

# Create /etc/hosts
cat > ./etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Copy Raspi device trees
cp ./usr/lib/firmware/5.15.0-1060-raspi/device-tree/broadcom/bcm2711*.dtb ./boot/
# Copy device tree overlays
cp -R ./usr/lib/firmware/5.15.0-1060-raspi/device-tree/overlays ./boot/
# Copy raspi firmware
cp ./usr/lib/linux-firmware-raspi/* ./boot/

# Copy kernel as the expected name
cp ./boot/vmlinuz-* ./boot/kernel8.img || true
# Copy initrd as the expected name
cp ./boot/initrd.img-* ./boot/initramfs8 || true

# Delete the symlinks
rm ./boot/vmlinuz || true
rm ./boot/initrd.img || true
```

The shared _config_root.sh_ creates a hostname and hosts file, and makes sure the kernel, bootloader and device trees are available at the expected location and name.

## EBcL Raspberry Pi 4 systemd image

The folder _images/arm64/raspberry/pi4/systemd_ contains the _systemd_ variant of the Raspberry Pi 4 image. This image is not a minimal one, but brings what you expect to find in a Raspberry Pi server image. Since we use the split archive feature, we install also the kernel and bootloader package to the root filesystem, which feels a bit simpler and we don’t need to care about the needed kernel modules, but also give a bit more bloated and less secure root filesystem.

```yaml
base: ../base.yaml
name: ebcl_pi4
packages:
  - linux-firmware-raspi
  - linux-raspi
  - u-boot-rpi
  - flash-kernel
  - systemd
  - systemd-coredump
  - systemd-timesyncd
  - udev
  - util-linux
  - netbase
  - locales
  - file
  - findutils
  - kmod
  - iproute2
  - iptables
  - iputils-ping
  - vim
  - nano
  - strace
  - apt
  - openssh-server
  - openssh-client
# Scripts to configure the root tarball
scripts:
  - name: ../config_root.sh # Name of the script, relative path to this file
    env: fake
  - name: config_systemd.sh # Name of the script, relative path to this file
    env: chroot
host_files:
  - source: ../cmdline.txt
    destination: boot
  - source: ../config.txt
    destination: boot
  - source: systemd_config/* # Crinit configuration
```

The common _config_root.sh_ is extended with a second, _systemd_ specific, _config_systemd.sh_ configuration file. This script links _systemd_ as init-manager and enables the basic system services for network, NTP and DNS. The _systemd_config_ overlay folder provides a basic system configuration, including apt and SSH.

## EBcL Raspberry Pi 4 crinit image

The _crinit_ variant of the Raspberry Pi 4 image, contained in _images/arm64/raspberry/pi4/crinit_, makes use of the _crinit_ init-manager, _elos_ for logging, and _netifd_ for the network configuration. It also comes with apt and SSH support, and provides typical tools like _vim_ or _strace_. The script _config_crinit.sh_ takes care of creating the machine ID, needed by _elos_, and makes sure DNS is working. All other configuration is provided as an overlay in the _crinit_config_ folder.
