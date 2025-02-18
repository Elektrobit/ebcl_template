# EB corbos Linux example images for the Raspberry Pi 4

## EBcL 1.x Raspberry Pi 4 image

The EB corbos Linux example image for the Raspberry Pi 4 board is contained in _images/arm64/raspberry/pi4/ebcl_1.x_.

EB corbos Linux comes with development support for the Raspberry Pi 4. This means, you can use a Raspberry Pi 4 board for early development and demos, and you get support, but it's not qualified for mass production.
The Raspberry Pi 4 example images make use of the kernel and firmware packages provided by [Ubuntu Ports](http://ports.ubuntu.com/ubuntu-ports/). These repositories are specified in _images/common/raspberry/pi4/base.yaml_:

```yaml
# CPU architecture
arch: arm64
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
  # Get Latest Community Tested Package Fixes
  # This Repository is soley added for one reason:
  # The flash-kernel postinstall script will try to execute
  # and write files to memory. This will not work in our build env (chroot).
  # flash-kernel will not do this on a system that is running in EFI Mode and
  # in updated versions where it can detect the chroot environment better.
  # Try running 'ls /sys/firmware/efi' if you have this dir, you can remove
  # This apt_repo safely.
  - apt_repo: http://ports.ubuntu.com/ubuntu-ports
    distro: jammy-updates
    components:
      - main
      - universe
      - multiverse
      - restricted
```

Please not that the EB corbos Linux APT repository is enabled in parallel to the Ubuntu repositories.
This is in general possible, but the resulting image will contain the newer package versions form Ubuntu, 
which are not qualified with the EB corbos Linux configuration and config and compatibility issues may happen.
Please also be aware that _jammy-updates_ may provide upgraded libraries which are not supported with EB corbos Linux,
since we only base on _jammy-secuirty_, to minimize the impact of the security maintenance to existing solutions.

For booting, the Raspberry Pi expects to find a fat32 partition as first partition on the SD card,
and this partition is expected to contain the firmware and kernel binaries and devicetrees,
and some configuration files.
For this image, we make use of the split archive feature of _embdgen_.
This feature allows the distribution of the content of one tarball to multiple partitions.
The _images/common/raspberry/pi4/image.yaml_ gets the content of _build/ebcl_pi4.config.tar_,
and puts the content of the _/boot_ folder to the _boot_ partition
and puts the remaining content to the _root_ partition.

```yaml
# Partition layout of the image
# For more details see https://elektrobit.github.io/embdgen/index.html
contents:
  - name: archive
    type: split_archive
    archive: build/root.config.tar
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
      size: 5 GB
      content:
        type: ext4
        content: archive.root
```

The _commandline.txt_ and _config.txt_ are just taken from a prebuilt Raspberry Pi OS image.

The shared _config_root.sh_ creates a hostname and hosts file, and makes sure the kernel,
bootloader and device trees are available at the expected location and name.

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
cp ./usr/lib/firmware/5.15.0-*-raspi/device-tree/broadcom/bcm2711*.dtb ./boot/
# Copy device tree overlays
cp -R ./usr/lib/firmware/5.15.0-*-raspi/device-tree/overlays ./boot/
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

## Raspberry Pi 4 Jammy image

We also provide an example image for the Raspberry Pi 4 using Ubuntu Jammy.
This image description is contained in _images/arm64/raspberry/pi4/jammy_.
The main differences to the _ebcl_1.x_ image is that it makes use of the systemd init manager,
and the Ubuntu Jammy APT repositories.


## Raspberry Pi 4 Noble image

The Raspberry Pi 4 Noble image, defined in _images/arm64/raspberry/pi4/noble_,
is similar to the Raspberry Pi 4 Jammy image, but makes use of the Ubuntu Noble packages.
