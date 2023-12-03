# QEMU amd64 crinit image

The files in this folder can be used to provision a QEMU arm64 image with crinit as an init manager.

- appliance.kiwi: The image description used for image creation. 
    - In the preferences section you can see: 
        ```
         <type image="oem" filesystem="ext4" firmware="custom" initrd_system="none" bootpartition="true" bootpartsize="60" format="qcow2">
               <bootloader name="grub2"/>
        ```
         So we will get an oem image, meaning the system can resize itself after deployment. The Filesystem used for the root filesystem will be ext4, we will use a custom firmware. For initrd_system none is specified, so we will not use a initrd system builder. Grub2 will be used as a bootloader, you can find related grub.cfg in the root overlay. The format of the QEMU image will be qcow2.
    - In the user section we create the root user
    - In the packages section we add the kernel and packages for network, ssh, sudo and grub. We also add elos and crinit. We delete packages like systemd or dracut as we do not require them for this image.

- images.sh: This script runs directly after the preparation of the root tree. In this case we:
    - remove coreutils if a busybox replacement exists
    - Create /etc/hosts
    - Relink /var/lib/dhcp to /run to ensure a read-writeable location

- root/: This is the root overlay folder used for the image. Files and directories here will be copied into the image during the image creation. In the subfolder boot you can see the grub.cfg used for booting, in etc you can find the elos and the crinit config, some basic config for sudoers and configuration of the shell prompt, and in /usr/bin you will find the init script, that only calls crinit as the init manager.

- config.sh: The scripts runs after the root overlay was applied. It roughly:
    - Create license information
    - Turn grub-mkconfig into a noop, we want to use the cfg from the root overlay
    - Allow suid tools with busybox
    - Delete data not needed or wanted, like the initrd from the kernel

Further information:
- crinit: https://github.com/Elektrobit/crinit
- elos: https://github.com/Elektrobit/elos
- image descriptions: https://osinside.github.io/kiwi/image_description.html
