# The arm64 images

EB corbos Linux comes with arm64 based example images for rpi4 and nxp s32g boards at the moment.
To ease development and testing we also provide QEMU arm64 images.

For _arm64/qemu_ we provide example images for EB corbos Linux (EBcL) and for Ubuntu Jammy.
The difference between EBcl and Jammy is, that EBcL provides some additional components, like the _crinit_ init-manager and the _elos_ logging and event framework, and that EBcL provides a qualified security maintenance release every three months, while Jammy is proving updates continuously, using less strict qualification and documentation. Additionally there is an example image provided for application development. You can find more about application development in later chapters.


## The arm64 Jammy image

In _images/arm64/qemu/jammy_ you can find a basic example image demonstrating how to use the EB corbos Linux SDK.
This folder contains the configuration of the example, and makes use of the QEMU _images/qemu*.mk_ include makefiles.

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
arch: 'arm64'
```

The example makes use of the kernel “linux-image-generic”. This is a meta-package and always takes the latest available Ubuntu Jammy package.
The Canonical Ubuntu apt repositories are used to build the examples.

Note that the only difference to the corresponding amd64 image is the arch specification in the last line, all further yaml files for the arm64 Jammy image are identical to the amd64 QEMU jammy image, and hence documented already in the previous section.

## The arm64 EB corbos Linux images

EB corbos Linux (EBcL) is an embedded Linux distribution targeting automotive and other industrial embedded Linux solutions.
The main differences between EBcL and Ubuntu are the release and qualification handling, and some additional components added by EBcL which allow building more lightweight and better performing embedded images.
The code is again very similar to the amd64 QEMU images.

The differences for aarch64 are the adaption of the architecture in _base.yaml_ and in _*.mk_ files.

### Supported images

The following images are supported:

- aarch64 EB corbos Linux systemd image
- aarch64 EB corbos Linux crinit image

Their functionality and implementation is analog to the corresponding amd64 images.
