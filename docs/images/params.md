# Configuration parameters

The following list gives an overview of the supported configuration parameters for the EB corbos Linux build helper tools.
In the round brackets it is noted for which files which option is applicable.
Embdgen is developed separately, and the details and options for the storage specification is documented in the [embdgen documentation](https://elektrobit.github.io/embdgen/index.html).

- **base** _(boot/initrd/root/config)_  \[default: None \]: Parent configuration file.
If specified, the values from the parent file will be used if not otherwise specified in the current file.

- **arch** _(boot/initrd/root)_  \[default: arm64 \]: The CPU architecture of the target hardware.
The supported values are arm64, amd64 and armhf.

- **use_fakeroot** _(boot/initrd/root/config)_  \[default: False \]: Use fakeroot in the generator tools where possible, instead of _sudo_ and _chroot_. This may cause issues for edge-cases.

- **apt_repos** _(boot/initrd/root)_  \[default: None \]: A list of apt repositories to download the required Debian packages.
Example:

```yaml
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
```
In addition, an armored public key file or URL can be given as “key”, and a unarmored gpg file can be given as “gpg”, to authenticate the package sources.

- **use_ebcl_apt** _(boot/initrd/root)_  \[default: No \]: If yes, the public apt repository of the EB corbos Linux will be added.
By default, the latest release will be used if the _ebcl_version_ parameter is not given.
This is a convenience feature, but be aware that this public apt repository doesn’t provide customer specific or proprietary packages.

- **ebcl_version** _(boot/initrd/root)_  \[default: latest release \]: EB corbos Linux release version, for the automatically generated apt repository.

- **host_files** _(boot/initrd/root)_  \[default: None \]: Files to include from the host or container environment.
Example:

```yaml
host_files:
  - source: bootargs-overlay.dts
    destination: boot
  - source: bootargs.its
    destination: boot
```
The _destination_ is the path in the target root filesystem or chroot environment.
In addition, the parameters “mode”, to specify the mode of the file, “uid”, to specify the owner of the file, and “gid”, to specify the owning group of the file, can be used.

- **files** _(boot)_  \[default: None \]: Files to get as result from the chroot environment.
Example:

```yaml
files:
  - boot/vmlinuz*
  - boot/config*
```

These files can be part of an extracted Debian package, or result of a script executed in the chroot environment.

- **scripts** _(boot/initrd/root/config)_  \[default: None \]: The scripts which shall be executed.

```yaml
scripts:
  - name: config_root.sh
    env: chroot
```
The supported environments are “chroot”, to run the script in a chroot environment, “fake”, to run the script in a fakeroot environment, “sudo” to run the script with root privileges, or “shell” to run the script in a plain shell environment.
For “chroot” the script will be placed at “/” and executed from this folder.
For all other environments, the current work directory will be the folder containing the target environment.
In addition, parameters which are forwarded to the script can be provided as “params”.

- **template** _(initrd/root)_  \[default: None \]: A Jinja2 template to create a configuration.
In case of the _initrd generator_, a template for the init script can be provided.
In case of the _root generator_, a template for the kiwi-ng XML image specification can be provided.

- **name** _(boot/initrd/root)_  \[default: None \]: A name which is used in the filenames of the generated artifacts.

- **download_deps** _(boot/initrd)_  \[default: True \]: Download the dependencies of the specified packages.
This parameter must be True, to use e.g.
a meta-package for the kernel binary and modules.

- **base_tarball** _(boot/initrd)_  \[default: None \]: A base chroot environment for generating the boot artifacts and for the _initrd.img_. If no base chroot environment is given, a minimal busybox based environment will be used.

- **packages** _(boot/initrd/root/config)_  \[default: None \]: A list of packages.
For the _root generator_, these packages are installed in the base _debootstrap_ environment.
For the _initrd generator_, these packages will be downloaded, extracted and integrated into the resulting _initrd.img_.
For the _boot generator_, these packages will be downloaded and extracted to get the kernel binary.
 
- **kernel** _(boot/initrd/root)_  \[default: None \]: Name of the kernel package.
For the _initrd generator_, these packages will be downloaded and extracted to a temporary folder to get the required kernel modules.

- **tar** _(boot)_  \[default: True \]: Flag for packing the boot artifacts as a tarball.
If _embdgen_ is used to write the artifacts to an image, this will preserve the owner and mode of the artifacts.

- **busybox** _(initrd)_  \[default: busybox-static \]: Name of the busybox package for the minimal busybox environment.

- **modules** _(initrd)_  \[default: None \]: List of kernel modules to add and load from the _initrd.img_. Example:

```yaml
modules:
  - kernel/drivers/virtio/virtio.ko 
  - kernel/drivers/virtio/virtio_ring.ko 
  - kernel/drivers/block/virtio_blk.ko 
  - kernel/net/core/failover.ko 
  - kernel/drivers/net/net_failover.ko 
  - kernel/drivers/net/virtio_net.ko
```


- **root_device** _(initrd)_  \[default: None \]: Name of the root device to mount.

- **devices** _(initrd)_  \[default: None \]: List of device nodes to add.
Example:

```yaml
devices:
  - name: mmcblk1
    type: block
    major: 8
    minor: 0
  - name: console
    type: char
    major: 5
    minor: 1
```

In addition, the parameters “mode”, to specify the mode of the device node, “uid”, to specify the owner of the device node, and “gid”, to specify the owning group of the device node, can be used.

- **kernel_version** _(initrd)_  \[default: auto detected \]: The kernel version of the copied modules.

- **modules_folder** _(initrd)_  \[default: None \]: A folder in the host or container environment containing the kernel modules.
This can be used to provide modules from a local kernel build.
Example:

```yaml
modules_folder: $$RESULTS$$
```

The string ``$$RESULTS$$`` will be replaced with the path to the output folder, for all paths given in yaml config files of the build tools.

- **result_pattern** _(root)_  \[default: auto detected \]: A name pattern to match the build result, e.g.
*.tar.xz for kiwi-ng tbz builds.

- **image** _(boot/initrd/root/config)_  \[default: None \]: A kiwi-ng XML image description.
This parameter can be used to integrate old image descriptions into new build flows.

- **berrymill_conf** _(root)_  \[default: None \]: A _berrymill.conf_ used for _berrymill_ build.
If none is given, the configuration will be automatically generated using the provided apt repositories.
This parameter can be used to integrate old image descriptions into new build flows.

- **use_berrymill** _(root)_  \[default: True \]: Flag to use berrymill for kiwi-ng build.
If this flag is set to false, kiwi-ng will be called without the berrymill wrapper.


- **use_bootstrap_package** _(root)_  \[default: True \]: Flag if a bootstrap package shall be used for kiwi-ng builds.
If this flag is set to True, one of the specified repositories needs to provide the bootstrap package.

- **bootstrap_package** _(root)_  \[default: bootstrap-root-ubuntu-jammy \]: Name of the bootstrap package for the kiwi-ng build.

- **bootstrap** _(root)_  \[default: None \]: List of additional bootstrap packages for the kiwi-ng build.

- **kiwi_root_overlays** _(root)_  \[default: None \]: List of root overlay folders for the kiwi-ng build.

- **use_kiwi_defaults** _(root)_  \[default: True \]: If this flag is true, the “root” folder and the kiwi-ng config scripts next to the appliance.kiwi, will be provided to kiwi-ng.

- **kiwi_scripts** _(root)_  \[default: None \]: List of additional scripts which will be provided to kiwi-ng during the build.

- **kvm** _(root)_  \[default: True \]: Flag if KVM acceleration shall be used for kiwi-ng builds.

- **image_version** _(root)_  \[default: 1.0.0 \]: Image version for the generated kiwi-ng image description.

- **type** _(root)_  \[default: debootstrap \]: Type of the root filesystem generator to use.
The supported generators are "debootstrap" and "kiwi".

- **primary_repo** _(root)_  \[default: auto selected Ubuntu Jammy repository \]: The primary apt repository for the debootstrap or kiwi-ng build.
The main component of this repository is used for _debootstrap_.

- **primary_distro** _(root)_  \[default: jammy \]: The name of the distribution used for _debootstrap_.

- **root_password** _(root)_  \[default: linux \]: The root password of the generated root filesystem.

- **hostname** _(root)_  \[default: ebcl \]: The hostname of the generated root filesystem.

- **domain** _(root)_  \[default: elektrobit.com \]: The domain name of the generated root filesystem.

- **console** _(root)_  \[default: auto configured \]: The console parameter of the generated root filesystem.
If none is given, “ttyS0,115200” is used for amd64, and “ttyAMA0,115200” is used for amd64.

- **sysroot_packages** _(boot/initrd/root/config)_  \[default: None \]: List of additional packages which shall be installed for sysroot builds.
This can be used to add additional development headers.

- **sysroot_defaults** _(boot/initrd/root/config)_  \[default: True \]: Flag if the default additional packages for sysroot builds shall be added.
If yes, in addition to the specified packages the packages “build-essential” and “g++” will be added.

