# The amd64 images

EB corbos Linux doesn’t support any amd64 hardware at the moment, but we provide some QEMU amd64 images.
Using amd64 for development may help to make your development flow much smoother since you don’t have to handle the tricky aspects of cross-building.

For _amd64/qemu_ we provide example images for EB corbos Linux (EBcL) and for Ubuntu Jammy.
The difference between EBcl and Jammy is, that EBcL provides some additional components, like the _crinit_ init-manager and the _elos_ logging and event framework, and that EBcL provides a qualified security maintenance release every three months, while Jammy is proving updates continuously, using less strict qualification and documentation.

## The amd64 Jammy images

In _images/amd64/qemu/jammy_ you can find five basic example images demonstrating how to use the EB corbos Linux SDK.
This folder contains the common configuration shared by all the examples, and makes use of the QEMU _images/qemu*.mk_ include makefiles.

```yaml
# Kernel package to use
kernel: linux-image-generic
# Apt repositories to use
apt_repos:
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy
    components:
      - main
      - universe
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy-security
    components:
      - main
      - universe
# CPU architecture
arch: 'amd64'
```

All examples make use of the kernel “linux-image-generic”. This is a meta-package and always takes the latest available Ubuntu Jammy package.
The Canonical Ubuntu apt repositories are used to build the examples.

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

All examples make use of a very simple image consisting of a gpt partition table and a single ext4 root partition with a size of 2 GB.

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Root device to mount
root_device: /dev/vda1
# List of kernel modules
modules:
  - kernel/drivers/block/virtio_blk.ko # virtio_blk is needed for QEMU
```

Also the _initrd.img_ is shared by all examples.
It first loads the virt-IO block driver and then mounts _/dev/vda1_ as the root filesystem.

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Download dependencies of the kernel package - necessary if meta-package is specified
download_deps: true
# Files to copy from the packages
files:
  - boot/vmlinuz*
  - boot/config*
# Do not pack the files as tar - we need to provide the kernel binary to QEMU
tar: false
```

The _boot.yaml_ is also not image specific.
It’s used to download and extract the kernel binary.
In addition, the kernel config is extracted.

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
    env: chroot # Type of execution environment - chfake means fakechroot
```

The _root.yaml_ shares the common parts of the root filesystem configuration of all these example images.
All examples use “ubuntu” as name, by default have a minimal root filesystem only consisting of _debootstrap_ and _systemd_, _udev_, and _util-linux_ additionally installed, and use the _config_root.sh_ as configuration, which links _systemd_ as _/sbin/init_.

### The amd64 Jammy berrymill image

At the moment, the EBcL SDK makes use of two more generic Linux root filesystem builders, _debootstrap_ and _kiwi-ng_. The default is _debootstrap_, because it provides a much better build speed, but also the previously used _kiwi-ng_ is still supported.
Future EBcL major release lines may drop _kiwi-ng_ and come with a more embedded optimized solution, so ideally you make use of the _root.yaml_ instead of using an own kiwi-ng XML image description.

The _amd64/qemu/jammy/berrymill_ image makes use of the above mentioned configurations, and extends it with an own _root.yaml_ and a specific _Makefile_.

```yaml
# Config to use as a base
base: ../root.yaml
# Add the EB corbos Linux apt repo to provide the bootstrap package
use_ebcl_apt: true
# Overwrite the image builder type - ensure kiwi is used
type: kiwi
# Pattern to match the result file
result_pattern: '*.tar.xz'
```

This _root.yaml_ inherits the _root.yaml_ from the parent folder, described above, and adds the EBcL apt repository, which provides the required kiwi-ng bootstrap package, set the build type to “kiwi” and updates the build result search pattern to “*.tar.xz”, since there is no way to disable the result compression with _kiwi-ng_.

```make
# Makefile for Jammy QEMU amd64 image using kiwi

# Arch for sysroot extraction
arch = x86_64

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec = root.yaml
# Specification of the initrd.img
initrd_spec = ../initrd.yaml
# Specification of the kernel
boot_spec = ../boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = ../config_root.sh


#--------------------
# Generated artifacts
#--------------------

# Disc image
disc_image = $(result_folder)/image.raw

# Base root tarball
base_tarball = $(result_folder)/ubuntu.tar.xz

# Configured root tarball
root_tarball = $(result_folder)/ubuntu.config.tar

# Generated initrd.img
initrd_img = $(result_folder)/initrd.img

# Kernel image
kernel = $(result_folder)/vmlinuz

# Sysroot tarball
sysroot_tarball = $(result_folder)/ubuntu_sysroot.tar


#-------------------
# Run the QEMU image
#-------------------

# QEMU kernel command line
kernel_cmdline_append = "rw"


# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_x86_64.mk
```

The _Makefile_ point _make_ to the right specification files, sets the flag to mount the root filesystem as writable, and includes the base makefiles describing how to build an QEMU image and how to run the build results using QEMU.

### The amd64 Jammy debootstrap image

In general, _kiwi-ng_ can also build images using debootstrap instead of a pre-built bootstrap package.
This brings the limitation that only one apt repository is supported, which needs to provide a proper main component, and that a _debootstrap_ script must be available in the build VM for the selected distribution.
The EBcL SDK can make use of this for Ubuntu Jammy builds, and the image _amd64/qemu/jammy/debootstrap_ is a proof of concept showing how to do it.

```yaml
# CPU architecture
arch: amd64
# Name of tarball
name: ubuntu
# APT repo for kiwi build
apt_repos:
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy
    components:
      - main
      - universe
# Use debootstrap instead of bootstrap package
# This allows us to use only one apt repo.
use_bootstrap_package: false
# Select required bootstrap packages
bootstrap:
  - apt
# Packages to install in the root tarball
packages:
  - systemd
  - udev
  - util-linux
# Overwrite the image builder type - ensure kiwi is used
type: kiwi
# Pattern to match the result file
result_pattern: '*.tar.xz'
# Scripts to configure the root tarball
scripts:
  - name: ../config_root.sh # Name of the script, relative path to this file
    env: chroot # Type of execution environment
```

The _root.yaml_ configures the Ubuntu Jammy apt repository as the single apt repository to use, and sets the “use_bootstrap_package” to false, which will result in a kiwi-ng build not relying on the EBcL bootstrap package.

### The amd64 Jammy debootstrap image

The _images/amd64/qemu/jammy/debootstrap_ image makes use of the _debootstrap_ root filesystem builder.
The only difference to the shared configuration is that _debootstrap_ is explicitly selected.

```yaml
# Config to use as a base
base: ../root.yaml
# Overwrite the image builder type - ensure debootstrap is used
type: debootstrap
```
The _Makefile_ is similar to the one above.

### The amd64 Jammy kernel source image

The _amd64/qemu/jammy/kernel_src_ image is a proof of concept showing how to make use of local compiled kernels with EBcL builds.
The _boot.yaml_ is used to get the kernel configuration of the Ubuntu Jammy kernel.
The _initrd.yaml_ extends the shared _initrd.yaml_ with the line “modules_folder: ``$$RESULTS$$``. The parameter “modules_folder” can be used to provide kernel modules from the host environment, and the string ``$$RESULTS$$`` will be replaced with the path to the build folder.

The _Makefile_ extends the default QEMU makefile with a bunch of new make targets.

```make
#--------------------------
# Image build configuration
#--------------------------

$(source):
	@echo "Get kernel sources..."
	mkdir -p kernel
	cd kernel && apt -y source linux
	sudo apt -y build-dep linux
	cd $(kernel_dir) && chmod +x scripts/*.sh

$(kconfig): $(boot_spec) $(source)
	@echo "Get kernel config as $(kconfig)..."
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(boot_spec) $(result_folder) 2>&1 | tee $(kconfig).log
	@echo "Renaming $(result_folder)/config-* as $(kconfig)..."
	mv $(result_folder)/config-* $(kconfig)
	@echo "Copying $(kconfig) to $(kernel_dir)..."
	cp $(kconfig) $(kernel_dir)/.config
	@echo "Set all not defined values of the kernel config to defaults..."
	cd $(kernel_dir) && yes "" | $(MAKE) $(kernel_make_args) olddefconfig
	@echo "Copying modified config as olddefconfig..."
	cp $(kernel_dir)/.config $(result_folder)/olddefconfig

$(kernel): $(kconfig) $(source)
	@echo "Get kernel binary..."
	cd $(kernel_dir) && yes "" | $(MAKE) -j 16 bzImage
	cd $(kernel_dir) && INSTALL_PATH=../../$(result_folder) $(MAKE) install
	cp -v $(result_folder)/vmlinuz-* $(kernel)
	@echo "Results were written to $(kernel)"

$(modules): $(kernel)
	@echo "Get virtio driver..."
	cd $(kernel_dir) && $(MAKE) -j 16 modules
	cd $(kernel_dir) && chmod +x debian/scripts/sign-module
	mkdir -p $(result_folder)
	cd $(kernel_dir) && INSTALL_MOD_PATH=../../$(result_folder) $(MAKE) modules_install

$(initrd_img): $(initrd_spec) $(modules)
	@echo "Build initrd.img..."
	mkdir -p $(result_folder)
	set -o pipefail && initrd_generator $(initrd_spec) $(result_folder) 2>&1 | tee $(initrd_img).log

#--------------------
# Helper make targets
#--------------------

# Rebuild the kernel binary
.PHONY: rebuild_kernel
rebuild_kernel:
	mkdir -p $(result_folder)
	cd $(kernel_dir) && yes "" | $(MAKE) -j 16 bzImage
	cd $(kernel_dir) && INSTALL_PATH=../../$(result_folder) $(MAKE) install
	cp -v $(result_folder)/vmlinuz-* $(kernel)
	@echo "Results were written to $(kernel)"

# Rebuild the kernel modules
.PHONY: rebuild_modules 
rebuild_modules: kernel
	mkdir -p $(result_folder)
	cd $(kernel_dir) && $(MAKE) modules -j 16
	cd $(kernel_dir) && chmod +x debian/scripts/sign-module
	rm -rf build/lib
	cd $(kernel_dir) && INSTALL_MOD_PATH=../../$(result_folder) $(MAKE) modules_install
```

The ``$(source)`` is responsible for fetching the kernel sources using apt, and installing the kernel build dependencies.
The ``$(kconfig)`` target gets the default config for the used kernel package and adds it to the kernel source tree.
 The ``$(kernel)`` target describes how to compile the kernel and get the kernel binary.
The ``$(modules)`` describes how to build and install the modules to the results folder.
The new make for the _initrd.img_ adds the dependency to the locally built kernel modules.

Overall, these new rules describe how to fetch the kernel sources and build the kernel binary and modules.
These binaries are then picked up by the default QEMU build flow and make rules.

### The amd64 Jammy kiwi image

The EBcL SDK makes by default use of _berrymill_ for _kiwi-ng_ builds, but it also supports using _kiwi-ng_ directly.
The image description in _amd64/qemu/jammy/kiwi_ is a proof of concept how to use _kiwi-ng_ without _berrymill_. Setting the flag “use_berrymill” to false does the trick.
This build variant has some limitations compared to the _berrymill_ build.
Derived images are not supported, and the current implementation doesn’t use apt repository authentication.



## The amd64 EB corbos Linux images

EB corbos Linux (EBcL) is an embedded Linux distribution targeting automotive and other industrial embedded Linux solutions.
The main differences between EBcL and Ubuntu are the release and qualification handling, and some additional components added by EBcL which allow building more lightweight and better performing embedded images.

```yaml
# Kernel package to use
kernel: linux-image-generic
use_ebcl_apt: true
# Additional apt repos
apt_repos:
  # Get latest security fixes
  - apt_repo: http://archive.ubuntu.com/ubuntu
    distro: jammy-security
    components:
      - main
      - universe
# CPU architecture
arch: 'amd64'
```

Again, the _base.yaml_ is used to define the kernel package, the apt repos and the CPU architecture.
The EBcL repo can be added using the “use_ebcl_apt” flag.
For experimenting and if we want the latest security patches without qualification, we can add the Ubuntu Jammy repositories.

The _boot.yaml_ is not different to the one used for the Jammy images, and just extracts the kernel binary and configuration form the given kernel package.
The _image.yaml_ and the _initrd.yaml_ are also identical to the ones used with the Jammy images.

### The amd64 EB corbos Linux systemd images

EBcL supports the _systemd_ init-manager and if startup time and the resource footprint are not too critical, it’s a quite good choice because all of the Ubuntu packages are fully compatible with it, and all services come with their configs for _systemd_. To run _systemd_ without providing the init-manager using the kernel command line, we can link it as _/sbin/init_. This is done using the _config_root.sh_ script.

#### The amd64 EB corbos Linux systemd berrymill image

The _amd64/qemu/ebcl/systemd/berrymill_ defines a QEMU image using _berrymill_ and _kiwi-ng_ for building the root filesystem.
This root filesystem is a very minimal one, only providing _systemd_, _udev_ and the default command line tools.

#### The amd64 EB corbos Linux systemd debootstrap image

The _amd64/qemu/ebcl/systemd/debootstrap_ defines a QEMU image using _debootstrap_ for building the root filesystem.
This root filesystem is a very minimal one, only providing _systemd_, _udev_ and the default command line tools.

### The amd64 EB corbos Linux crinit images 

EBcL adds [crinit](https://github.com/Elektrobit/crinit) init-manger, as an alternative to _systemd_. [Crinit](https://github.com/Elektrobit/crinit) is a much more lightweight init-manager, compared with _systemd_, and tailored to embedded.
Since all the hardware and use-cases are very well known in advance for an embedded system, many dynamic configuration and detection features of _systemd_ can be skipped, which results in a faster and much more lightweight solution.
The drawback of using _crinit_ is that the Ubuntu packages are not prepared for _crinit_, and all service and startup configuration needs to be done by the user.

The necessary minimal configuration to use _crinit_ is contained in _images/amd64/qemu/ebcl/crinit/crinit_config_, and this folder is copied as overlay to the root filesystem using the _root.yaml_. The script _config_root.sh_ ensures that the _sbin/init_ script, provided in the overlay, is executable.
Instead of _systemd_, _crinit_ and its command line client _crinit-ctl_ is installed.

Let’s take a closer look at the _crinit_config_ overlay.
The _sbin/init_ mounts the _/proc_ filesystem and then runs the _crinit_ init-manager.
The _/etc_ folder contains a minimal _crinit_ configuration.
The file _/etc/crinit/default.series_ is the main configuration file, and the folder _/etc/crinit/crinit.d_ contains the services we want to run.
The task _/etc/crinit/crinit.d/agetty-ttyS0.crinit_ runs _agetty_ on the serial console _ttyS0_, so that we can login using the QEMU serial console.
The task _/etc/crinit/crinit.d/earlysetup.crinit_ sets the hostname, so that we get proper logs.
The task _/etc/crinit/crinit.d/mount.crinit_ takes care of mounting the additional filesystems.

#### The amd64 EB corbos Linux crinit berrymill image

The _amd64/qemu/ebcl/crinit/berrymill_ defines a QEMU image using _berrymill_ and _kiwi-ng_ for building the root filesystem.
This root filesystem is a very minimal one, only providing _crinit_.

#### The amd64 EB corbos Linux crinit debootstrap image

The _amd64/qemu/ebcl/crinit/debootstrap_ defines a QEMU image using _debootstrap_ for building the root filesystem.
This root filesystem is a very minimal one, only providing _crinit_.

### The amd64 EB corbos Linux server images

The previous images were all very minimal images, only providing enough to boot and login to the system.
For developing an embedded system this is the right place to start development, but for exploring and playing with the system it’s too less.
The server images provide a more complete user experience and add logging, network, _apt_ and _ssh_.

#### The amd64 EB corbos Linux server crinit image

The _crinit_ variant of the server image is contained in _images/amd64/qemu/ebcl/server_. In addition to _crinit_, it provides the [elos](https://github.com/Elektrobit/elos) logging and event manager, which is a lightweight replacement of _journald_ and _dbus_, which allows automatic log evaluation and event handling.
To manage the network interfaces, _netifd_ from the OpenWRT world is used.
It’s a very powerful and nevertheless lightweight network manager used in many router solutions.
Als NTP client _ntpdate_ is used.
To allow remote login _openssh-server_ is added.
The image also contains _apt_ to allow easy installation of additional packages, and the typical Linux tools and editors for playing and exploring.

The _root_common.yaml_ is the shared root specification of all the EBcL server variants.
It defines the name, the architecture and the common tools and services, like _openssh-server_. The _root.yaml_ extends the package list with the _crinit_ and _elos_ specific packages, and defines the overlay for the _crinit_ configuration and the config script for the _crinit_ variant.
This _config_root.sh_ sets a machine ID, required by _elos_, and generates a _/etc/hosts_ file.

Let’s take a look at the server configuration.
In addition to the _/usr/sbin/init_, which runs _crinit_, a _ntp_time.sh_ is provided.
This _ntp_time.sh_ does a one-shot NTP time update, as soon as the network is up, to avoid issues with apt and other time sensitive services.
The _/etc/apt_ folder provides the apt repository configuration for EBcL and Ubuntu Jammy.
The file _/etc/config/network/network_ is evaluated by _netifd_ to bring up the network interfaces.
This configuration makes use of an static IPv6 and a dynamic IPv4 configuration.
The _crinit_ tasks are extended with tasks to run _elos_, bring up the network, run the SSH service, and trigger the NTP time update.
The file _/etc/elos/elosd.json_ contains some basic _elos_ configuration, to use it as syslog demon.
The config _/etc/ssh/sshd_config.d/10-root-login.conf_ enables SSH login is root.
The config _/etc/gai.conf_ ensures that IPv4 DNS is preferred over IPv6. The other config files just set some reasonable defaults.

#### The amd64 EB corbos Linux server systemd image

The folder _images/amd64/qemu/ebcl/server/systemd_ contains a variant of the EBcL server image using _systemd_ as init manager.
It’s mainly provided as a reference, to compare the configuration and performance.
