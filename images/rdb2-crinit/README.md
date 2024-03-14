# Raspberry Pi image

The files in this folder can be used to provision a NXP RDB2 aarch64 image with crinit as an init manager.

- `appliance.kiwi`: The image description used for image creation. 
    - In the preferences section you can see: 
        ```xml
         <type image="oem" filesystem="ext2" firmware="custom" initrd_system="dracut" bootpartition="true" bootpartsize="300" editbootinstall="uboot-install.sh" bootfilesystem="fat32" disk_start_sector="8192">
            <bootloader name="custom"/>
        ```
         So we will get an [oem](https://osinside.github.io/kiwi/image_types_and_results.html) image. The filesystem type used for the root filesystem will be ext2, and we will use a fat32 boot partition. The bootloader will be the NPX RDB2 specific bootloader. The format of the image will be raw, which is the default.
    - In the user section we create the root user and the ebcl user
    - In the packages section we add the NXP RDB2 specific firmware and kernel, and packages for network, ssh and sudo.

- `config.sh`: This script runs directly after the preparation of the root tree. In this case we:
    - set the base runlevel for systemd
    - generate the license information for the installed packages
    - allow suid tools from busybox
    - link systemd as init manager and configure systemd

- `post_bootstrap.sh`: Configure dracut.

- `pre_disk_sync.sh`: Prepare RDB2 boot config.

- `uboot-install.sh`: Setup u-boot bootloader for RDB2.

- `root/`: This is the root overlay folder used for the image. Files and directories here will be copied into the image during the image creation.

Further information:
- crinit: https://github.com/Elektrobit/crinit
- elos: https://github.com/Elektrobit/elos
- image descriptions: https://osinside.github.io/kiwi/image_description.html
