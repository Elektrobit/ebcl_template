# NXP RDB2 systemd image

The files in this folder can be used to provision a NXP RDB2 image with systemd as an init manager.

- `appliance.kiwi`: The image description used for image creation. 
    - In the preferences section you can see: 
        ```xml
         <type image="oem" filesystem="ext2" firmware="custom" initrd_system="dracut" bootpartition="true" bootpartsize="300" editbootinstall="uboot-install.sh" bootfilesystem="fat32" disk_start_sector="8192">
            <bootloader name="custom"/>
        ```
         So we will get an [oem](https://osinside.github.io/kiwi/image_types_and_results.html) image. The filesystem type used for the root filesystem will be ext2, and we will use a custom firmware. For initrd will be generated using dracut. The bootloader will be a U-Boot based NXP RDB2 specific bootloader. The format of the image will be raw, which is the default.
    - In the user section we create the root user and the ebcl user
    - In the packages section we add the NXP RDB2 specific firmware and kernel, and packages for network, ssh, and sudo.

- `root/`: This is the root overlay folder used for the image. Files and directories here will be copied into the image during the image creation. In the subfolder boot you can see the grub.cfg used for booting, in etc you can find some basic config for sudoers and configuration of the shell prompt.

- `config.sh`: The scripts runs after the root overlay was applied. It roughly:
    - Configures systemd
    - Create license information
    - Allow suid tools with busybox
    - Link systemd as init manager and finalize the systemd configuration

- `post_bootstrap.sh`: This script configures dracut.

- `pre_disk_sync.sh`: This script before creation of the disk image. In this case we:
    - Create /etc/hosts
    - Relink /var/lib/dhcp to /run to ensure a read-writeable location
    - Update the license data
    - Config time and DNS
    - Prepare the NXP bootloader and firmware

- `uboot-install.sh`: Create the fip image containing firmware and U-Boot.


Further information:
- image descriptions: https://osinside.github.io/kiwi/image_description.html

## APT

The image has apt preconfigured, so you can easily install additional packages in the running system for testing.
For production, please add the packages to the image description and rebuild the image.

- `root/etc/apt/sources.list`: This file configures the Elektrobit APT repository as package source.
- `root/etc/apt/trusted.gpg.d/ebcl_1.0.gpg`: This is the public part of the Elektrobit APT repository signing key, so that APT can proove that the packages are valid.
