# NXP-S32G2-CRINIT
This image was created in respect to a refernce image design documented here: https://infohub.automotive.elektrobit.com/pages/viewpage.action?spaceKey=PRJEBLINUX&title=EBcL+PI+2024-01
It shall fit the role of **vm-registry** as described in the rough overall architecture of the reference image.

## Configuration
A superficial overview of some configuration files and the neccassity of certain config


### Network

#### root/etc/crinit/crinit.net.d
A subfolder of the crinit configuration folder which contains network specifc service files. Crinit **does not** recognize
the naming of the subfolder, rathers it was choosen for a better understanding for maintainers.
##### static.crinit
Spawns the netif Daemon responisible for network communication and setup. It passes a valid resolv.conf and a network config file
to the Daemon. It is **required** that **all** network services associated with netif depend on a running ubus daemon.

with static.crinit a static IPv4 network setup is spawned. It is important to note, that crinit **will not** read this service file,
before it is not placed in **etc/crinit/crinit.d/.**. Then and only then will it be executed by crinit. The last line of
**pre_disk_sync.sh** takes care of this when building the image via symlinking it to the right location. 

##### dhcp.crinit
Does all the same things as static.crinit only that its being passed a dhcp network configuration. While not required by design
it is quite important for a QEMU environment. Here it can make use of the virtual dhcp server of QEMU and communicate a 
generic IP-address for every users specfic environment. The actual Hardware Image will not make use of this crinit service.

#### root/etc/config
Contains network configuration files for static and dhcp.

##### network-dhcp/network
network configuration file for the dhcp.crinit service. Configures a loopback network device for localhost services with the name **lo**
and the eth0 device with an interface which in turn enables dhcp address lookup.
**eth0** is just a variable as well as **lan** and **lo**, **loopback**. 

##### network-static/network
network configuration file for the static.crinit service. Similar configuration only with the lan interface 
defining a **static IPv4** IP address, a default gateway and one DNS Server (Google's)

#### pre_disk_sync.sh
the package netifd delivers the file **resolv.conf.netifd**, places it under **/var/run** and links it to 
**/etc/resolv.conf**. Kiwi **will drop** this resolv.conf on cleanup. Thus, it is important to **relink** the deliverd
resolv conifig to the systemwide file responsible for DNS Nameresoultion Lookup /etc/resolv.conf.
The pre disk sync script takes care of this as the last step of the rootfs generation.


### SSH

#### root/etc/crinit/crinit.d/sshd.crinit
Responsible for spawning the ssh daemon on system startup **after** ubus has spawned to take care of message
handling and bus service registration. The daemon needs a **writable** directory for temporary runtime information, which here 
is created under /run, which is always writeable and available before other filesytems are mounted. The Kernel will mount 
/run as runfs.

#### root/etc/ssh/sshd_config.d
Contains two config files for enabling ssh root login and change the listening port of the daemon as required by design.
The naming does not matter as long as it ends in **.conf**. Files will be sourced into the daemon configuration
alphanumerical.


### LOGIN

#### root/etc/crinit/crinit.d/agetty-ttyAMA0.crinit
spawns tty daemon for key input and output for the shell. There are multiple flavors available of tty
and on QEMU virt arm system the **AMA0** flavor is required! Depending on the system this can vary 
and you should pay attention to it if you ever find yourself not able to login to the image.

#### root/profile.d/10-ash-prompt.sh

PS1='\u@\h:\w\$ ': this line sets the value of the PS1 variable. In Unix-like systems, PS1 is the primary prompt string variable used by the shell to display the command prompt. Here, \u represents the username, \h represents the hostname, \w represents the current working directory, and \$ represents the prompt character ($ for regular users, # for root).

So,this code sets the prompt to display the username, hostname, and current working directory followed by a $ prompt character.


### LOGGING

#### root/etc/crinit/crinit.d/elosd.crinit
spawns the Elos daemon.

#### root/etc/crinit/crinit.d/elos-coredump.crinit
Sawns elos coredump to handle kernel coredump, triggering events based on it and storing it to 
(default location) /tmp/. or /var/log/.

#### root/etc/elos/elosd.json
Elos daemon configuration file. YOu can research further information about it here:
https://elektrobit.github.io/elos/doc/userManual.htm

#### root/etc/cirint/crinit.d/mount.crinit
A tmpfs is mounted on /var/log because elos is storing its log json files there.
It is required by design that these logs reside in RAM rather than eMMC.

**alternatively elosd.json can be configured to store files in /tmp** 


### MOUNTING
I'll explain what hasn't been yet or isn't (hopefully) trivial.

#### root/etc/crinit/crinit.d/mount.crinit

- *ext4 /dev/vda2 /containers*: vda2 is the second partition of the virtual storage device used by QEMU.
                                It is created in the run-arm script and here mounted on the image 
- *rm -r /containers/tmp/*:     The fake tmp dir is cleaned on the **much larger** second partiton.
                                Podman can create quite huge tmp files. Too large for either RAM (no tmpfs) or
                                the rootfs partition. Podman cleanes up after itself so it is planned that this
                                directory will not be overfilling with a long operation time. Its cleaned on every
                                Startup to mimic a non persistant tmpfs.
- *tmpfs tmpfs /var/cache*:     See under Other


### PODMAN

#### root/run/containers/0/auth.json
Default location for podman to lookup and store authentication details for defined registries.
Here the authentication token of a **robot user** owned by **anba273315** on linux.elektrobit.com is used.

#### root/etc/containers/
Default directory to override default podman configuration by the system admin

##### ../containers.conf
Default location to override and set podmans parameters and options.
All necessary Info on what was changed is in the file. 

##### ../storage.conf
Override all default storage locations of podman to read,write partition /containers
All necessary Info on what was changed is in the file.

##### ../registries.conf
E.g: **podman pull ebcl/sdk** will be resolved as **podman pull linux.elektrobit.com/ebcl/sdk**

#### /etc/crinit/crinit.d/enable-tun.crinit
Read,Write Access for users needed for device /dev/net/tun to enable
rootless operation of container. slirp4netns needs permission to operate on this
virtual network simulator.

## Other
Take a close look at the files. Detailed comments on what does what can be found in each file.

### run-arm
A bash script for creating a .raw file for QEMU with two partitions (rootfs) and larger second 
partition (mounted on /containers).

You **must** have osc installed on your system to make use of this script. Osc checkout the 
project here https://ebs.ebgroup.elektrobit.com/package/show/nautilos:2.0:demo:nxps32g_hv_pfe/vm-timetracker.
The run-arm script is also there.
Set the executable bit for the script and run it. It will take care of booting the image 
with all the right parameters for Qemu.

**If you want to have a writable rootfs, append 'rw' (without parenthesis) to the -append parameter value**

### Mounting tmpfs of /var/cache/containers
Podman does a short name aliasing when trying to pull unqualified containers e.g. (podman pull ebcl/sdk)

Short-Name Aliasing: Modes
The short-name-mode option supports three modes to control the behaviour of short-name resolution.

- enforcing:  If only one unqualified-search registry is set, use it as there is no ambigu‐
                ity.  If there is more than one registry and the user program is running  in  a  terminal
                (i.e.,  stdout    stdin are a TTY), prompt the user to select one of the specified search
                registries.  If the program is not running in a terminal, the  ambiguity  cannot  be  re‐
                solved which will lead to an error.

- permissive: Behaves as enforcing but does not lead to an error if the program is not run‐
                ning in a terminal.  Instead, fallback to using all unqualified-search registries.

- disabled: Use all unqualified-search registries without prompting.

If short-name-mode is not specified at all or left empty, default to the permissive mode.  If  the
user-specified  short name was not aliased already, the enforcing and permissive mode if prompted,
will record a new alias after a successful pull.  Note that the recorded alias will be written  to
/var/cache/containers/short-name-aliases.conf for root to have a clear separation between possibly
human-edited registries.conf files and the machine-generated short-name-aliases-conf.   Note  that
$HOME/.cache  is  used for rootless users.  If an alias is specified in a registries.conf file and
also the machine-generated short-name-aliases.conf, the short-name-aliases.conf  file  has  prece‐
dence.

Mounting tmpfs needed because /var/cache/containers is readonly
