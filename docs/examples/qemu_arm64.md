# The example images

EB corbos Linux comes with arm64 based example images for rpi4 and nxp s32g boards at the moment.
To ease development and testing we also provide QEMU arm64 images.

For _arm64/qemu_ we provide example images for EB corbos Linux (EBcL) and for Ubuntu Jammy and Ubuntu Noble.
The difference between EBcl and Ubuntu is, that EBcL provides some additional components, like the _crinit_ init-manager and the _elos_ logging and event framework, and that EBcL provides a qualified security maintenance release every three months, while Jammy is proving updates continuously, using less strict qualification and documentation. Additionally there is are amd64 and arm64 example image provided for application development. You can find more about application development in later chapters.

## Build-flow for QEMU images

QEMU requires three artifacts to run an image. These artifacts are a _kernel_ binary,
a _initrd.img_ binary, and a disc image providing a root filesystem.
The build flow, to get these artifacts, is the same for all QEMU images,
and we defined it in _images/tasks/QEMU_image.yml_.

```yaml
...
  build:
    desc: Build and run the qemu image
    cmds:   
      - task: boot:extract_kernel
      - task: root:build
      - task: root:config
      - task: initrd:build
      - task: embdgen:build
    method: none
...
```

The build steps are:

- The _boot:extract_kernel_ task of the _BootGenerator.yml_ runs the _boot_generator_ to extract the kernel.
- The _root:build_ task of the _RootGenerator.yml_ runs the _root_generator_ to install the defined packages.
- The _root:config_ task of the _RootGenerator.yml_ runs the _root_generator_ to apply the configuration.
- The _initrd:build_ task of the _InitrdGenerator.yml_ runs the _initrd_generator_ build the _initrd.img_.
- The _embdgen:build_ task of the _Embdgen.yml_ runs the _Embdgen_ to generate the _image.raw_ disc image.

This generic QEMU build task is used by all QEMU images.

## The ebcl_1.x QEMU image

In _images/arm64/qemu/ebcl_1.x_ you can find a basic example image demonstrating
how to use the EB corbos Linux SDK. The _root.yml_ and the _boot.yaml_ and _initrd.yaml_ include
the common _images/common/qemu/arm64/base.yaml_, which defines the kernel package and the
APT repositories used by all QEMU arm64 EBcL images.

The _boot.yaml_ further includes the _images/common/qemu/boot.yaml_, which describes how to extract
the kernel binary in an architecture independent way.
Using this includes makes reading the specification a bit harder to ready,
but it is a really good way to avoid redundancy and simplify the maintenance of related images.

The _initrd.yaml_ includes the common _images/common/qemu/initrd.yaml_ and _images/common/qemu/initrd_jammy.yaml_ files.
The file _images/common/qemu/initrd.yaml_ defines the common parts of all _initrd.img_ used by QEMU,
and the file _images/common/qemu/initrd_jammy.yaml_ adds some specifics for the images based on the EBcL 1.x and Ubuntu 22.04 packages.
There is another _images/common/qemu/initrd_noble.yaml_ which does the same for the EBcL 2.x and Ubuntu 24.04 packages.

The _root.yaml_ includes the common _images/common/arm64/crinit/root.yaml_.
This file describes the common root filesystem configuration for all arm64 images using the crinit init manager,
and also brings in the common _crinit_ and _elos_ runtime configuration.

These includes mechanism and hierarchy allows to structure the runtime configuration of an image
as reusable features, similar to the layer mechanism used by Yocto, and the sharing of these configurations
allows building up a base of easy usable features, which can be easily integrated in any Debian package
based image, using our SDK approach.

Lets take a close look at these configuration fragments.
The file _images/common/qemu/arm64/base.yaml_ looks like:

```yaml
# CPU architecture
arch: 'arm64'
# Kernel package to use
kernel: linux-image-generic
use_ebcl_apt: true
```

This yaml file defines the used target architecture as _arm64_, and the used kernel package as _linux-image-generic_.
The line `use_ebcl_apt: true` is a convenience function to specify the EB corbos Linux public APT repository,
and it makes use of the _arch_ parameter.
The kernel package specification is used by the _boot_generator_, to find the right deb package containing the kernel binary,
and by the _initrd_generator_ to decide which kernel modules ar used.

The file _images/common/qemu/boot.yaml_ looks like:

```yaml
# Download dependencies of the kernel package - necessary if meta-package is specified
download_deps: true
# Files to copy from the packages
files:
  - boot/vmlinuz*
  - boot/config*
# Do not pack the files as tar - we need to provide the kernel binary to QEMU
tar: false
```

The _download_deps_ parameter enables the download of packages specified as dependencies in the Debian package metadata.
Setting this flag to true allow using a meta-package like _linux-image-generic_, instead of a specific kernel version.
The _files_ define a list of glob-matches for files which shall be copied to the build folder.
This is used to make the kernel binary available for QEMU, and also to get the kernel configuration for information and inspection.
If the _tar_ parameter is set to true, the extracted file will be put into a tar archive,
which helps to preserve the file attributes, but is not needed for using the kernel with QEMU.

The file _images/common/qemu/initrd.yaml_ looks like:

```yaml
# Root device to mount
root_device: /dev/vda1
# List of kernel modules
modules:
  # virtio modules
  - virtio_blk
  - failover
  - net_failover
  - virtio_net
  # graphics support
  - sysimgblt
  - sysfillrect
  - syscopyarea
  - fb_sys_fops
  - drm
  - drm_kms_helper
template: init.sh
packages:
  # Tools for checking ext4 partitions.
  - e2fsprogs
```

It specifies the root device as `/dev/vda1` and a bunch of kernel modules required for full QEMU support.
Without _virtio_blk_, the boot for QEMU would fail, because the root partition is provided as VirtIO device.
The _template_ parameter allows to provide a user specific `init.sh` script,
and the path is relative to the configuration file.
You can find the used script at _images/common/qemu/init.sh_.
The package _e2fsprogs_ to fix an ext4 filesystem which was mounted in an unclean way,
and without this tools in the _initrd.img_, you can brick your image by killing QEMU or doing a power cut.
Please be aware that the _initrd_generator_ only extracts the packages and not runs any install scripts.
We handle it this way, because our initrd is intended to be as small as possible,
and therefore misses a lot of packages which are expected to be available for any Debian root filesystem.

The file _images/common/qemu/initrd_jammy.yaml_ add a bunch of additional kernel modules,
required for the the firewall, Docker, Podman, graphics support and systemd.

```yaml
# List of kernel modules
modules:
  # virtio modules
  - veth
  # bridge support - requried by dockerd and podman
  - br_netfilter
  # nttabes kernel modules - required by dockerd and podman
  - nft_compat
  - xt_addrtype
  - nft_counter
  - nf_conntrack_netlink
  - nft_chain_nat
  - xt_conntrack
  - xt_comment
  - xt_MASQUERADE
  - overlay
  - xfrm_user
  # dm-verity modules
  - dm-verity
  # graphics support
  - cec
  - virtio-gpu
  # systemd
  - autofs4
```

The file _images/common/arm64/crinit/root.yaml_ looks like:

```yaml
base: ../root.yaml
# Additional packages for the crinit variant
packages:
  # Init manager
  - crinit
  - crinit-ctl
  # Elos for logging
  - elos
  - elos-coredump
  - elos-plugin-backend-json
  - elos-plugin-backend-dummy
  - elos-plugin-scanner-kmsg
  - elos-plugin-scanner-syslog
  - elos-plugin-scanner-shmem
  - elos-plugin-client-tcp
  # Network manager
  - netifd
  - udhcpc
  - netbase
  # NTP time client
  - ntpdate
# Crinit configuration
host_files:
  - source: config/*
# Scripts to configure the root tarball
scripts:
  - name: config_root.sh # Name of the script, relative path to this file
    env: chroot # Type of execution environment
```

It adds the _crinit_ and _elos_ specific packages, and the common packages defined in _images/common/root.yaml_.
Please be aware that the file _images/common/root.yaml_ resets the kernel package because we don't want to have it
installed in the root filesystem.
The _host_files_ and the _scripts_ specify the runtime configuration for the packages, which is added during the
root filesystem configuration step. These parameters also support glob, and the paths are also relative to the yaml file.

## The arm64 Jammy image

In _images/arm64/qemu/jammy_ you can find a basic example image demonstrating how to use the EB corbos Linux SDK
to build images for other Debian distributions.
It makes use of _images/common/qemu/arm64/jammy.yaml_, which looks like:

```yaml
# CPU architecture
arch: 'arm64'
# Kernel package to use
kernel: linux-image-generic
# CPU architecture
apt_repos:
  - apt_repo: http://ports.ubuntu.com/ubuntu-ports
    distro: jammy
    components:
      - main
      - universe
  - apt_repo: http://ports.ubuntu.com/ubuntu-ports
    distro: jammy-security
    components:
      - main
      - universe
  - apt_repo: http://ports.ubuntu.com/ubuntu-ports
    distro: jammy-updates
    components:
      - main
      - universe
```

The difference to the _ebcl_1.x_ image is, that instead of the EB corbos Linux apt repositories,
the Ubuntu Jammy arm64 APT repositories are used.
The _boot_ and _initrd_ specifications are identical to the _ebcl_1.x_ image,
only the _root_ specification is different, because the _systemd_ init manager instead of _crinit_ is used.
Additionally, another config folder is specified, which overwrites the `/etc/hostname` file form the common configuration.

## The arm64 Noble image

The arm64 Ubuntu Noble image is identical to the arm64 Ubuntu Jammy image, except two deviations.
Instead of the Jammy APT repositories, the Noble APT repositories are specified in _images/common/qemu/arm64/noble.yaml_,
in for the initrd, instead of the Jammy specific kernel modules, the Noble specific kernel modules are used.

This image also gives an example how easy EB corbos Linux images can be upgraded to newer versions
or even other base distributions. The restriction that the packages are considered as the smallest
building blocks of a image, and that no patching or re-compiling is allowed, results in a highly reduced
maintenance effort.
