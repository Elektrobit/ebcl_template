# EBcL SDK container

The EBcL SDK container allows an EBcL user to:

- Build a customer apps form source (gcc and cmake)
- Configure, modify and build an ECU images (arm64 and amd64)
- Run ECU images in QEMU (arm64 and amd64)

ToDo:
- Package a customer apps as Debian source package (dsc)
- Package a customer apps as Debian binary package (deb, arm64 and amd64)

## Container mount points

- `/build/app`: mount point for app source code. Default: Symlink to `/build/workspace/app` for dev container usage
- `/build/img`: mount point for appliance image description. Default: Symlink to `/build/workspace/images` for dev container usage
- `/build/sysroot_aarch64`: mount point for the aarch64 sysroot. Default: Symlink to `/build/workspace/sysroot_aarch64` for dev container usage
- `/build/sysroot_amd64`: mount point for the amd64/x86_64 sysroot. Default: Symlink to `/build/workspace/sysroot_amd64` for dev container usage
- `/build/result_image`: mount point for the image build output folder. Default: Symlink to `/build/workspace/result/image` for dev container usage
- `/build/result_app`: mount point for the app build output folder. Default: Symlink to `/build/workspace/result/app` for dev container usage


## Commands

Prepare sysroot:

- `prepare_sysroot.sh`: Native Berrymill prepare run to get sysroot for amd64/x86_64. This command requires a privileged container.
- `box_build_sysroot.sh`: Berrymill box build using derived images to create a tbz of the root filesystem for amd64.
- `cross_build_sysroot.sh`: Berrymill box build using derived images to create a tbz of the root filesystem for aarch64.

Build app:

- `cmake_amd64.sh`: Use cmake to build app for amd64/x86_64 environment.
- `cmake_aarch64.sh`: Use cmake to build app for aarch64 environment.

Build image:

- `kvm_build_image.sh`: Berrymill image box build for amd64/x86_64 using kvm acceleration. This command requires a privileged container.
- `box_build_image.sh`: Berrymill image box build for amd64/x86_64 without acceleration.
- `cross_build_image.sh`: Berrymill image box build for aarch64.

- `build_image.sh`: Native Berrymill image build. This command requires a privileged container.

This command is not working at the moment. Error:

```bash
[ INFO    ]: 09:55:51 | Creating raw disk image /tmp/result_image/ebcl_1.0/ebcl_1.0.x86_64-1.0.0.raw
[ DEBUG   ]: 09:55:51 | EXEC: [qemu-img create /tmp/result_image/ebcl_1.0/ebcl_1.0.x86_64-1.0.0.raw 2864M]
[ DEBUG   ]: 09:55:51 | EXEC: [losetup -f --show /tmp/result_image/ebcl_1.0/ebcl_1.0.x86_64-1.0.0.raw]
[ DEBUG   ]: 09:55:51 | "grub2-install": in paths "/tmp/result_image/ebcl_1.0/build/image-root/build/venv/bin:/tmp/result_image/ebcl_1.0/build/image-root/build/scripts:/tmp/result_image/ebcl_1.0/build/image-root/home/ebcl/.local/bin:/tmp/result_image/ebcl_1.0/build/image-root/usr/local/sbin:/tmp/result_image/ebcl_1.0/build/image-root/usr/local/bin:/tmp/result_image/ebcl_1.0/build/image-root/usr/sbin:/tmp/result_image/ebcl_1.0/build/image-root/usr/bin:/tmp/result_image/ebcl_1.0/build/image-root/sbin:/tmp/result_image/ebcl_1.0/build/image-root/bin" exists: "False" mode match: not checked
[ DEBUG   ]: 09:55:51 | Initialize gpt disk
[ DEBUG   ]: 09:55:51 | EXEC: [sgdisk --zap-all /dev/loop23]
[ INFO    ]: 09:55:56 | --> creating EFI CSM(legacy bios) partition
[ DEBUG   ]: 09:55:56 | EXEC: [sgdisk -n 1:2048:+2M -c 1:p.legacy /dev/loop23]
[ DEBUG   ]: 09:55:57 | EXEC: [sgdisk -t 1:EF02 /dev/loop23]
[ INFO    ]: 09:55:58 | --> creating EFI partition
[ DEBUG   ]: 09:55:58 | EXEC: [sgdisk -n 2:0:+20M -c 2:p.UEFI /dev/loop23]
[ DEBUG   ]: 09:55:59 | EXEC: [sgdisk -t 2:EF00 /dev/loop23]
[ INFO    ]: 09:56:00 | --> creating SWAP partition
[ DEBUG   ]: 09:56:00 | EXEC: [sgdisk -n 3:0:+128M -c 3:p.swap /dev/loop23]
[ DEBUG   ]: 09:56:02 | EXEC: [sgdisk -t 3:8200 /dev/loop23]
[ INFO    ]: 09:56:03 | --> using all_freeMB for the root(rw) partition if present
[ INFO    ]: 09:56:03 | --> creating root partition [with 0 clone(s)]
[ DEBUG   ]: 09:56:03 | EXEC: [sgdisk -n 4:0:0 -c 4:p.lxroot /dev/loop23]
[ DEBUG   ]: 09:56:04 | EXEC: [sgdisk -t 4:8300 /dev/loop23]
[ DEBUG   ]: 09:56:05 | EXEC: [partx --add /dev/loop23]
[ ERROR   ]: 09:56:05 | KiwiError: KiwiMappedDeviceError [Device /dev/loop23p1 does not exist]
[ INFO    ]: 09:56:05 | Cleaning up Disk instance
[ DEBUG   ]: 09:56:05 | EXEC: [partx --delete /dev/loop23]
[ DEBUG   ]: 09:56:05 | EXEC: Failed with stderr: partx: /dev/loop23: error deleting partitions 1-3
, stdout: (no output on stdout)
[ WARNING ]: 09:56:05 | cleanup of partition device maps failed, /dev/loop23 still busy
[ INFO    ]: 09:56:05 | Cleaning up LoopDevice instance
```

TODO: Test outside of contianer. Maybe privilege issue.

Helper commands:

- `berrymill_root.sh`: Run Berrymill as root
- `qemu_efi_aarch64.sh`: Run a qcow2 aarch64 image including and efi bootloader in QEMU.
- `qemu_efi_amd64.sh`: Run a qcow2 amd64/x86_64 image including and efi bootloader in QEMU.

Util commands:

- `env.sh`: Setup environment. Must get sourced.
- `init.sh`: Container entrypoint
- `prepare_image_build.sh`: Prepares an image build. Copies the selected image to `/tmp/img`.

## Manual usage

- Create Docker volume for boxes: `docker volume create ebcl_sdk_boxes`
- Run container using workspace template:

```bash
docker run --rm -it \
    -v ${PWD}:/build/workspace:rw \
    -v ebcl_sdk_boxes:/home/ebcl/.kiwi_boxes:rw \
    linux.elektrobit.com/ebcl/sdk:latest
```

Alternative you can provide the needed mountpoints one by one.

## Berrymill quick start

Berrymill is an appliance generator of root file systems for embedded devices. It is a wrapper around kiwi-ng and allows to build bare metal EB corbos Linux ECU images. For more details about Berrymill see https://github.com/isbm/berrymill.

Berrymill is pre-installed in the EBcL SDK container. To build an image form an image description, run the container using: `docker run --rm -it -v <path to image description>:/build/img:ro -v <path to result folder>:/build/result:rw linux.elektrobit.com/ebcl/sdk:latest`. In the container, you can run Berrymill using the command `berrymill`.

If you want to build images for the same architecture as our build host, and if you are able to run a privileged Docker container, you can use the native build. To run the container in privileged mode, use `docker run --privileged --rm -it -v <path to image description>:/build/img:ro -v <path to result folder>:/build/result:rw linux.elektrobit.com/ebcl/sdk:latest`.

For native building, you also need to run Berrymill with root rights. You can do this by using `berrymill_root.sh` instead of using `berrymill`.

## Build a customer app from source

The SDK container contains gcc, cross-gcc, make and cmake for building customer applications.
To build an application, a fitting sysroot folder for the ECU image is needed, to ensure that the shared libraries match the libraries used in the ECU image.

### Preparing a sysroot folder

To prepare a sysroot folder, the used image description must be bind-mounted into the container as `/build/img`, then the sysroot can be prepared using the `prepare_sysroot.sh` script.

The resulting sysroot is copied to `/build/sysroot`. Please be aware that all old content of `/build/sysroot` is deleted during the build.

#### Example: sysroot for amd64/x86_64

Run the container:

```bash
$ docker run --privileged --rm -it \
  -v ${PWD}/images/test-image:/build/img:ro \
  -v ${PWD}/sysroot_amd64:/build/sysroot_amd64:rw \
  linux.elektrobit.com/ebcl/sdk:latest
```

The image should be mounted read-only to avoid unintended modification by container commands. The `--priviledged` flag is mandatory for Berrymill native builds, since Berrymill is using mount commands.

In the container, you can trigger the native sysroot creation by running: `./prepare_sysroot.sh`. The result is written to `/build/sysroot_amd64`.

If usage of a privileged container is not possible, use `box_build_sysroot.sh` instead.

#### Example: sysroot for aarch64

To prepare a sysroot for aarch64, we can use `cross_build_sysroot.sh`. This script utilizes the Berrymill derived image feature to prepare the sysroot.

Run the container:

```bash
$ docker run --rm -it \
  -v ${PWD}/images/test-image:/build/img:ro \
  -v ${PWD}/sysroot_aarch64:/build/sysroot_aarch64:rw \
  linux.elektrobit.com/ebcl/sdk:latest
```

In the container, you can trigger the sysroot creation by running: `cross_build_sysroot.sh`. The result is written to `/build/sysroot_aarch64`.

### Build the app

Please make sure you first create a sysroot, or bind-mount your sysroot as `/build/sysroot_<image architecture>`.

To build your app, you need to bind-mount the sources as `/build/app`.

#### C application

A simple C hello-world app is contained in `./test-apps/hello_world`.

Run the container: 

```bash
$ docker run --rm -it \
    -v ${PWD}/test-apps/hello_world:/build/app:ro \
    -v ${PWD}/sysroot_amd64:/build/sysroot_amd64:ro \
    -v ${PWD}/sysroot_aarch64:/build/sysroot_aarch64:ro \
    -v ${PWD}/result:/build/result:rw \
    linux.elektrobit.com/ebcl/sdk:latest
```

##### Using GCC

amd64/x86_64:

```bash
gcc -o /build/result/app /build/app/main.c --sysroot /build/sysroot_amd64
```

aarch64:

```bash
aarch64-linux-gnu-gcc -o /build/result/app /build/app/main.c --sysroot /build/sysroot_aarch64
```

##### Using cmake

amd64/x86_64:

```bash
cmake --toolchain /build/cmake/toolchain-amd64.cmake -B ./result_app -S ./app
cd /build/result
make
```

aarch64:

```bash
cmake --toolchain /build/cmake/toolchain-aarch64.cmake -B /build/result -S /build/app
cd /build/result
make
```

#### C++ application

A simple C++ app using a library is contained in `./test-apps/with_lib`.

This app is using `libjsoncpp`.
To be able to build the app, we need to make the package `libjsoncpp-dev` available in the image.
For the productive, we just need the library and not the headers. This is the package `libjsoncpp25`.
So, if we want to use this app in your image, we need to add the package `libjsoncpp25` to the productive image.
To get the right sysroot to build the app, we can use the Berrymill feature of derived images.
An example which just adds `libjsoncpp-dev` is contained in `./images/test-image/appliance_sysroot.kiwi`.

To build the sysroot, run the container: 

```bash
$ docker run --rm -it \
    -v ${PWD}/test-image:/build/img:ro \
    -v ${PWD}/sysroot_amd64:/build/sysroot:rw \
    -v ${PWD}/boxes:/home/ebcl/.kiwi_boxes:rw \
    linux.elektrobit.com/ebcl/sdk:latest
```

Then, run the sysroot creation providing the extended appliance.
For aarch64 this is done with: `./cross_build_sysroot.sh appliance_sysroot.kiwi`.

##### Using GCC

amd64/x86_64:

```bash
 g++-11 -o /build/result/app /build/app/main.cpp --sysroot /build/sysroot/ -I /build/sysroot/usr/include/jsoncpp -ljsoncpp
```

aarch64:

Run the container:

```bash
$ docker run --rm -it \
    -v ${PWD}/sysroot_aarch64:/build/sysroot:ro \
    -v ${PWD}/test-apps/with_lib:/build/app:ro \
    -v ${PWD}/result:/build/result:rw \
    linux.elektrobit.com/ebcl/sdk:latest
```

```bash
 aarch64-linux-gnu-g++-11 -o /build/result/app /build/app/main.cpp --sysroot /build/sysroot/ -I /build/sysroot/usr/include/jsoncpp -ljsoncpp
```

##### Using cmake

amd64/x86_64:

```bash
cmake --toolchain /build/cmake/toolchain-amd64.cmake -B ./result_app -S ./app
cd /build/result
make
```

aarch64:

```bash
cmake --toolchain /build/cmake/toolchain-aarch64.cmake -B /build/result -S /build/app
cd /build/result
make
```

## Configure, modify and build an ECU images

The SDK container provides Berrymill as tool for building bare metal ECU images.

amd64/x86_64:

For amd64/x86_64 for can use the faster native build, which requires the privileged container.
Run the container:

```bash
 $ docker run --rm -it --privileged \
    -v ${PWD}/images/test-image:/build/img:ro \
    -v ${PWD}/result_image:/build/result_image:rw \
    -v ${PWD}/boxes:/home/ebcl/.kiwi_boxes:rw \
    linux.elektrobit.com/ebcl/sdk:latest
```

And run the build:

```bash
./build_image <name of appliance file>
```

If running a privileged container is not possible, or you run into other host environment issues, use the box build:

```bash
./box_build_image <name of appliance file>
```

aarch64:

Run the container:

```bash
 $ docker run --rm -it \
    -v ${PWD}/test-image:/build/img:ro \
    -v ${PWD}/result_image:/build/result_image:rw \
    -v ${PWD}/boxes:/home/ebcl/.kiwi_boxes:rw \
    linux.elektrobit.com/ebcl/sdk:latest
```

And run the build:

```bash
./cross_build_image <name of appliance file>
```

## Images with Hypervisor

Will be added soon!

## Using VS Code

To use the VS Code dev container, do:

- Install Docker, VS Code and the Dev Containers extension
- Open the workspace `./workspace/ebcl_sdk_1-0-0.code-workspace`
- Click in the blue button in the lower left corner of the VS Code window
- Click "Reopen in container"

This will download the linux.elektrobit.com/ebcl/sdk:latest Docker container image, run it as a Docker container and bind-mount your workspace into the container.

Then you can prepare the sysroot, build the app and build the image using the provided VS Code tasks.

### Dev container config

The VS Code dev container config can be found in `./workspace/.devcontainer/devcontainer.json`.

### Tasks

A example for a VS Code task to prepare the sysroot for amd64/x86_64 using the image "images/default" form the workspace folder is:

```json
{
    "type": "shell",
    "label": "sysroot default x86_64",
    "command": "box_build_sysroot.sh",
    "args": [ "default/appliance.kiwi" ],
    "options": {
    "cwd": "/build/img"
    },
    "group": {
    "kind": "build"
    },
    "detail": "Prepare sysroot for default image x86_64."
}
```

Tasks are defined in `./workspace/.vscode/tasks.json`.

The VS Code dev container is configured to run non-privileged, so only the box-build of Berrymill can be used.

If your host supports privileged containers, and you want to use native Berrymill builds, change the privileged flag in `./workspace/.devcontainer/devcontainer.json`:

```json
"privileged": false,
```