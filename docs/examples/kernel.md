# Kernel development

If you do the bring-up for a new board, you may need to adapt the kernel configuration.
This section continues where "Building an image from scratch" ended.

Please be aware that EB corbos Linux allows you to “open the box”, but if you modify the provided binary packages the support and maintenance for these packages is not covered with the base offer.
You can get support, qualification and long term maintenance as an add-on to the base offer, as a yearly fee for each package.

Nevertheless, let’s see how we can build our own kernel.
To build a custom kernel package we need the kernel sources and the base kernel config.
We can get the kernel sources and build dependencies using apt:

```bash
mkdir -p kernel
cd kernel
apt -y source linux-buildinfo-5.15.0-1034-s32-eb
sudo apt -y build-dep linux-buildinfo-5.15.0-1034-s32-eb
```

For extracting the kernel config, we can again make use of the _boot generator_:

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Do not pack the files as tar
tar: false
# download and extract the kernel package incl. depends
use_packages: true
# Files to copy to the build folder
files:
  - boot/config*
```

We can copy this config as _.config_ into the kernel source and build the kernel using task.

To make use of our local built kernel binary we need and adapted _boot.yaml_:

```yaml
# Derive values from base.yaml - relative path
base: base.yaml
# Reset the kernel value - we don't want to download and extract it
kernel: null
# Do not pack the files as tar
tar: false
# do not download and extract these packages, they are already installed in the boot_root.tar
use_packages: false
# Name of the boot root archive
base_tarball: $$RESULTS$$/boot_root.tar
# Files to copy form the host environment
host_files:
  - source: ../bootargs-overlay.dts
    destination: boot
  - source: ../bootargs.its
    destination: boot
  - source: $$RESULTS$$/initrd.img
    destination: boot
  - source: $$RESULTS$$/vmlinuz
    destination: boot
# Scripts to build the fitimage and fip.s32
scripts:
  - name: ../build_fitimage.sh # Build the fitimage in the boot_root.tar environment
    env: chroot
# Files to copy to the build folder
files:
  - boot/fip.s32
  - boot/fitimage
```

The only change compared to the old _boot.yaml_ is that we add ``$$RESULTS$$/vmlinuz`` to the _host_files_. This means our kernel binary is copied to the _/boot_ folder of the fitimage build environment, and will overwrite the one from the kernel Debian package.
This will give us the following build flow:

![S32G2](../assets/S32G2_kernel.png)

We can add this to our _Taskfile_ with the following changes:

```yaml
version: '3'

vars:
  arch: 'aarch64'
  partition_layout: ../image.yaml
  root_filesystem_spec: root.yaml
  initrd_spec: ../initrd.yaml
  boot_spec: boot.yaml
  boot_root_spec: ../boot_root.yaml
  config_root: config_root.sh
  base_tarball: build/ebcl_rdb2.tar
  root_tarball: build/ebcl_rdb2.config.tar
  sysroot_tarball: build/ebcl_rdb2_sysroot.tar
  kernel_config: kernel_config.yaml
  kernel_package: linux-buildinfo-5.15.0-1034-s32-eb
  build_fitimage: ../build_fitimage.sh
  fitimage_config: ../bootargs.its
  bootloader_config: ../bootargs-overlay.dts
  kernel: build/vmlinuz
  modules: build/lib
  kconfig: build/config
  source: kernel
  kernel_dir: kernel/linux-s32-eb-5.15.0
  kernel_make_args: ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-

includes:
   
    taskfile: ../rdb2.yml
    flatten: false

tasks:
  source:
    cmds:
      - echo "Get kernel sources..."
      - mkdir -p {{.source}}
      - cd {{.source}} && apt -y source {{.kernel_package}}
      - sudo apt -y build-dep {{.kernel_package}}
      - cd {{.kernel_dir}} && chmod +x scripts/*.sh
    generates:
      - ./{{.source}}

  kconfig:
    cmds:
      - echo "Get kernel config..."
      - mkdir -p {{.result_folder}}
      - set -o pipefail && boot_generator {{.kernel_config}} {{.result_folder}} 2>&1 | tee {{.kconfig}}.log
      - echo "Deleting old {{.kconfig}}..."
      - rm -f {{.kconfig}} || true
      - echo "Renaming {{.result_folder}}/config-* as {{.kconfig}}..."
      - mv {{.result_folder}}/config-* {{.kconfig}} || true
      - echo "Copying {{.kconfig}} to {{.kernel_dir}}..."
      - cp {{.kconfig}} {{.kernel_dir}}/.config
      - echo "Set all not defined values of the kernel config to defaults..."
      - cd {{.kernel_dir}} && make {{.kernel_make_args}} olddefconfig
      - echo "Copying modified config as olddefconfig..."
      - cp {{.kernel_dir}}/.config {{.result_folder}}/olddefconfig
    sources: 
       - ./{{.kernel_config}}
    generates: 
       - ./{{.kconfig}}

  build_kernel:
    cmds:
      - echo "Compile kernel..."
      - cd {{.kernel_dir}} && make {{.kernel_make_args}} -j 16 Image
      - echo "Get kernel binary..."
      - cp {{.kernel_dir}}/arch/arm64/boot/Image {{.kernel}}
      - echo "Results were written to {{.kernel}}"
    sources: 
       - ./{{.kconfig}}
    generates: 
       - ./{{.kernel}}

  build_modules:
    cmds:
      - echo "Get virtio driver..."
      - cd {{.kernel_dir}} && make {{.kernel_make_args}} modules -j 16
      - cd {{.kernel_dir}} && chmod +x debian/scripts/sign-module
      - mkdir -p {{.result_folder}}
      - cd {{.kernel_dir}} && INSTALL_MOD_PATH=../../{{.result_folder}} make {{.kernel_make_args}} modules_install
    generates:
      - ./{{.modules}}

  config_kernel:
    cmds:
      - cd {{.kernel_dir}} && make {{.kernel_make_args}} menuconfig
    preconditions:
      - test -d {{.kernel_dir}} 

  build_boot:
    cmds:
      - echo "Get fitimage..."
      - mkdir -p {{.result_folder}}
      - set -o pipefail && boot_generator {{.boot_spec}} {{.result_folder}} 2>&1 | tee {{.fitimage}}.log
    preconditions:
       - test -f {{.boot_spec}}
    sources:
       - ./{{.boot_spec}}
       -  /{{.boot_root}}
       - ./{{.fitimage_config}}
       - ./{{.build_fitimage}}
    generates:
       - ./{{.fitimage}}

  rebuild_boot:
    cmds:
      - mkdir -p {{.result_folder}}
      - cd {{.kernel_dir}} && make {{.kernel_make_args}} -j 16 Image
      - echo "Delete the old kernel binary..."
      - rm -f {{.kernel}}
      - echo "Get the new kernel binary..."
      - cp {{.kernel_dir}}/arch/arm64/boot/Image {{.kernel}}
    preconditions:
      - test -d {{.kernel_dir}}
      - test -f {{.kconfig}}
    generates:
      - ./{{.kernel}}

  rebuild_modules:
    cmds:
      - mkdir -p {{.result_folder}}
      - cd {{.kernel_dir}} && make {{.kernel_make_args}} modules -j 16
      - cd {{.kernel_dir}} && chmod +x debian/scripts/sign-module
      - echo "Delete the old kernel modules..."
      - rm -rf {{.modules}}
      - echo "Install the new kernel modules..."
      - cd {{.kernel_dir}} && INSTALL_MOD_PATH=../../{{.result_folder}} make {{.kernel_make_args}} modules_install
    preconditions:
      - test -d {{.kernel_dir}}
      - test -f {{.kconfig}}
    generates:
      - ./{{.modules}}

  clean:
    cmds:
      - task:  clean
      - rm -rf {{.source}}

  build_boot_root:
    cmds:
      - task:  build_boot_root

  build_image:
    cmds:
      - task: source
      - task: kconfig
      - task: build_kernel
      - task: build_modules
      - task: build_boot
      - task:  build_image
  
  build_initrd:
    cmds:
      - task:  build_initrd

  build_rootfs:
    cmds:
      - task:  build_rootfs

  edit_root:
    cmds:
      - task:  edit_root

  install_sysroot:
    cmds:
      - task:  install_sysroot

  mrproper:
    cmds:
      - task:  mrproper
      - task: clean

  sysroot_tarball:
    cmds:
      - task:  sysroot_tarball
```

