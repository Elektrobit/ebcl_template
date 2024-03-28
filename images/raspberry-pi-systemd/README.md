# Raspberry Pi systemd image

The files in this folder can be used to provision a Raspberry Pi 4 image with systemd as an init manager.

- `appliance.kiwi`: The image description used for image creation. 
    - In the preferences section you can see: 
        ```xml
         <type image="oem" filesystem="ext4" firmware="efi" initrd_system="none" bootpartition="false" efipartsize="128" devicepersistency="by-label" editbootinstall="editbootinstall_rpi.sh">
            <bootloader name="custom"/>
        ```
         So we will get an [oem](https://osinside.github.io/kiwi/image_types_and_results.html) image. The filesystem type used for the root filesystem will be ext4, and we will use a efi firmware partition. For initrd_system none is specified, since we have to use the Raspberry Pi kernel, intird and firmware. The bootloader will be also the Raspberry Pi specific bootloader. The format of the image will be raw, which is the default.
    - In the user section we create the root user and the ebcl user
    - In the packages section we add the Raspberry Pi specific firmware and kernel, and packages for network, ssh, and sudo.

- `root/`: This is the root overlay folder used for the image. Files and directories here will be copied into the image during the image creation. In the subfolder boot you can see the grub.cfg used for booting, in etc you can find some basic config for sudoers and configuration of the shell prompt.

- `config.sh`: The scripts runs after the root overlay was applied. It roughly:
    - Create license information
    - Turn grub-mkconfig into a noop, since we want to use the cfg from the root overlay
    - Allow suid tools with busybox
    - Configuration for systemd like activation of services
    - install the Raspberry Pi firmware from deb-packages we have added using the root overlay folder
    - add some Raspberry Pi specific configruation

- `pre_disk_sync.sh`: This script before creation of the disk image. In this case we:
    - remove coreutils if a busybox replacement exists
    - Create /etc/hosts
    - Relink /var/lib/dhcp to /run to ensure a read-writeable location
    - copy the Raspberry Pi firmware and device trees to _/boot/efi_
    - copy the Raspberry Pi kernel  to _/boot/efi_
    - setup u-boot bootloader

- `editbootinstall_rpi.sh`: Change the partition table from GPT to MBR, which is needed for the Raspberry Pi.


Further information:
- image descriptions: https://osinside.github.io/kiwi/image_description.html

## APT

The image has apt preconfigured, so you can easily install additional packages in the running system for testing.
For production, please add the packages to the image description and rebuild the image.

- `root/etc/apt/sources.list`: This file configures the Elektrobit APT repository as package source.
- `root/etc/apt/trusted.gpg.d/ebcl_1.0.gpg`: This is the public part of the Elektrobit APT repository signing key, so that APT can proove that the packages are valid.
