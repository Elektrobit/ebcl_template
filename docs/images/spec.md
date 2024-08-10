# Image specification

Let's take a look at this QEMU build flow in detail, and see how the details of this solution are specified and the roles of the different build helper tools.

![Embedded Systems](../assets/QEMU_flow.drawio.png)

Let’s take a look at this from left to right. The _base.yaml_ specifies the common aspects of all the generated artifacts. It configures the kernel package, the used apt repositories and the target CPU architecture.

```yaml
# Kernel package to use
kernel: linux-generic
# Apt repositories to use
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
# CPU architecture
arch: arm64
```

The boot.yaml builds on top of the base.yaml. It specifies to download the dependencies of the used kernel package, which is necessary if a meta-package is used, and it specifies that the config* and vmlinuz* files from the boot folder shall be used as results. The tar flag specifies that the results shall not be bundled as a tarball, but instead directly copied to the output folder. The boot generator is the helper tool allowing such kind of build steps.

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Download dependencies of the kernel package - necessary if meta-package is specified
download_deps: true
# Files to copy from the packages
files:
  - source: boot/vmlinuz*
    destination:           # Empty means root folder
  - source: boot/config*
    destination: 
# Do not pack the files as tar - we need to provide the kernel binary to QEMU
tar: false

```

The initrd images created by the tooling from the server and desktop world are very flexible and complete from a feature set point of view, but completely bloated form an embedded point of view. Since we know our target hardware and software in detail, we don’t need flexibility, but typically we want to have the best startup performance we can squeeze out of the used hardware. The inird generator is a small helper tool to build a minimal initrd.img, to get the best possible startup performance. It also helps to fast and easily customize the initrd content. One important reason why this is a separate helper tool, is that we don’t want to bloat the root filesystem with tooling for initrd image generation.

The initrd specification also derives the values from the base.yaml, and specifies that the /dev/vda1 shall be used as device for the root filesystem. Since the Canonical default kernel has no built-in support for virtio block devices, we have to load the driver in the initrd image, to be able to mount the root filesystem. This is done by specifying the kernel module in the modules list. Because of this line, the inird generator will download and extract the specified kernel package and its dependencies, detect the kernel version, get the right module, add it to the initrd image and load it before mounting the root filesystem. How this works in detail will be described in the later chapters.

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Root device to mount
root_device: /dev/vda1
# List of kernel modules
modules:
  - kernel/drivers/block/virtio_blk.ko # virtio_blk is needed for QEMU
```

The root.yaml describes the used root filesystem. It doesn’t need to contain a kernel, since the kernel is provided separately to QEMU. For Debian based distributions, a minimal set of required packages are specified by the used base distribution, in our case Canonical. These packages are installed automatically, and we only need to specify what we want to have on top. In this case, its systemd as init manager, udev to create the device nodes, and util-linux to provide the basic CLI tools. In addition, a config script is specified which adapts the configuration to our needs. This script is executed in a fakechangeroot environment. The name is use for naming the resulting tarball of the root filesystem.

```yaml
# Derive the base configuration
base: base.yaml
# Reset the kernel - should not be installed
kernel: null
# Name of the archive.
name: ubuntu
# Packages to install in the root tarball
packages:
  - systemd
  - udev        # udev will create the device node for ttyS0
  - util-linux
# Scripts to configure the root tarball
scripts:
  - name: config_root.sh # Name of the script, relative path to this file
    env: chfake # Type of execution environment - chfake means fakechroot

```

The build flow is using the root generator and the root configurator. The root generator can be told to not take care of the configuration steps, and these steps can be executed as a separate step afterwards. This is not necessary, but a development usability improvement. For real world root filesystems, the package installation step may require more than 10 minutes, while the configuration step only requires seconds. This split allows us  to skip this base installation step if only the configuration was changed.

The last step is to convert the root tarball into a disc image. The storage layout is specified in the image.yaml, and is picked up by embdgen. For the QEMU image we use a simple gpt partition table base image with only one partition. This partition is using the ext4 file format, has a size of 2 GB, and is filled with the contents of our root tarball.

```yaml
# Partition layout of the image
# For more details see https://elektrobit.github.io/embdgen/index.html
image:
  type: gpt
  boot_partition: root

  parts:
    - name: root
      type: partition
      fstype: ext4
      size: 2 GB
      content:
        type: ext4
        content:
          type: archive
          archive: build/ubuntu.config.tar
```

All together, we have a complete specification of our embedded solution, targeting QEMU as our virtual hardware.
