# QEMU x86_64 crinit image

The files in this folder can be used to provision a QEMU x86_64 image with crinit as an init manager.

- `appliance.kiwi`: The image description used for image creation. 
    - In the preferences section you can see: 
        ```xml
         <type image="oem" filesystem="ext4" firmware="custom" initrd_system="none" format="qcow2">
            <bootloader name="grub2"/>
        ```
         So we will get an [oem](https://osinside.github.io/kiwi/image_types_and_results.html) image. The filesystem type used for the root filesystem will be ext4, and we will use a custom firmware. For initrd_system none is specified, so we will not use a initrd system builder. Grub2 will be used as a bootloader. You can find related grub.cfg in the root overlay. The format of the QEMU image will be qcow2.
    - In the user section we create the root user and the ebcl user
    - In the packages section we add the kernel and packages for network, ssh, sudo and grub. We also add elos and crinit. We delete packages like systemd or dracut as we do not require them for this image.

- `root/`: This is the root overlay folder used for the image. Files and directories here will be copied into the image during the image creation. In the subfolder boot you can see the grub.cfg used for booting, in etc you can find the elos and the crinit config, some basic config for sudoers and configuration of the shell prompt, and in /usr/bin you will find the init script, that only calls crinit as the init manager.

- `config.sh`: The scripts runs after the root overlay was applied. It roughly:
    - Create license information
    - Turn grub-mkconfig into a noop, since we want to use the cfg from the root overlay
    - Allow suid tools with busybox

- `pre_disk_sync.sh`: This script before creation of the disk image. In this case we:
    - remove coreutils if a busybox replacement exists
    - Create /etc/hosts
    - Relink /var/lib/dhcp to /run to ensure a read-writeable location

Further information:
- crinit: https://github.com/Elektrobit/crinit
- elos: https://github.com/Elektrobit/elos
- image descriptions: https://osinside.github.io/kiwi/image_description.html

## Network

### root/etc/crinit/crinit.net.d

This subfolder of the crinit configuration folder contains network specifc service files. Crinit does not recognize
the naming of the subfolder, rathers it was choosen for a better understanding for maintainers.

#### static.crinit

Spawns the netif daemon responisible for network communication and setup. It passes a valid resolv.conf and a network config file
to the Daemon. It is required that allnetwork services associated with netif depend on a running ubus daemon.

With static.crinit a static IPv4 network setup is spawned. It is important to note, that crinit will not read this service file,
before it is not placed in _etc/crinit/crinit.d/_. Then and only then will it be executed by crinit. The last line of
_pre_disk_sync.sh_ takes care of this when building the image via symlinking it to the right location.

#### dhcp.crinit

Does all the same things as static.crinit only that its being passed a dhcp network configuration. While not required by design
it is quite important for a QEMU environment. Here it can make use of the virtual dhcp server of QEMU and communicate a
generic IP-address for every users specfic environment. The actual hardware image will not make use of this crinit service.

### root/etc/config

Contains network configuration files for static and dhcp.

#### network-dhcp/network

Network configuration file for the dhcp.crinit service. Configures a loopback network device for localhost services with the name _lo_
and the eth0 device with an interface which in turn enables dhcp address lookup.
_eth0_ is just a variable as well as _lan_, _lo_ and _loopback_.

#### network-static/network

Network configuration file for the static.crinit service. Similar configuration only with the lan interface
defining a static IPv4 IP address, a default gateway and one DNS Server (Google's)

#### pre_disk_sync.sh

The package netifd delivers the file _resolv.conf.netifd_, places it under _/var/run_ and links it to
_/etc/resolv.conf_. Kiwi will drop this resolv.conf on cleanup. Thus, it is important to relink the deliverd
resolv conifig to the systemwide file responsible for DNS Nameresoultion Lookup _/etc/resolv.conf_.
The pre disk sync script takes care of this as the last step of the rootfs generation.

## SSH

### root/etc/crinit/crinit.d/sshd.crinit

Responsible for spawning the ssh daemon on system startup after ubus has spawned to take care of message
handling and bus service registration. The daemon needs a writable directory for temporary runtime information, which here
is created under _/run_, which is always writeable and available before other filesytems are mounted. The Kernel will mount
_/run_ as runfs.

## LOGIN

### root/etc/crinit/crinit.d/agetty-ttyAMA0.crinit

Spawns tty daemon for key input and output for the shell. There are multiple flavors available of tty
and on QEMU virt arm system the _S0_ flavor is required! Depending on the system this can vary
and you should pay attention to it if you ever find yourself not able to login to the image.

### root/profile.d/10-ash-prompt.sh

PS1='\u@\h:\w\$ ': this line sets the value of the PS1 variable. In Unix-like systems, PS1 is the primary prompt string 
variable used by the shell to display the command prompt. Here, \u represents the username, \h represents the hostname,
\w represents the current working directory, and \$ represents the prompt character ($ for regular users, # for root).

So,this code sets the prompt to display the username, hostname, and current working directory followed by a $ prompt character.

## LOGGING

### root/etc/crinit/crinit.d/elosd.crinit

Spawns the Elos daemon.

### root/etc/crinit/crinit.d/elos-coredump.crinit

Spawns elos coredump to handle kernel coredump, triggering events based on it and storing it to
(default location) /tmp/ or /var/log/.

### root/etc/elos/elosd.json

Elos daemon configuration file. You can research further information about it here:
https://elektrobit.github.io/elos/doc/userManual.htm

### root/etc/cirint/crinit.d/mount.crinit

A tmpfs is mounted on /var/log because elos is storing its log json files there.
It is required by design that these logs reside in RAM rather than eMMC.

Alternatively elosd.json can be configured to store files in /tmp.

## APT

The image has apt preconfigured, so you can easily install additional packages in the running system for testing.
For production, please add the packages to the image description and rebuild the image.

- `root/etc/apt/sources.list`: This file configures the Elektrobit APT repository as package source.
- `root/etc/apt/trusted.gpg.d/ebcl_1.0.gpg`: This is the public part of the Elektrobit APT repository signing key, so that APT can proove that the packages are valid.
