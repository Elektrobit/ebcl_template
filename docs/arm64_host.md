# Using EB corbos Linux SDK on arm64

The EB corbos Linux SDK is primary developed and tested on amd64 Linux hosts,
but it is also possible to use it on arm64 hosts.
It was tested once on a Raspberry Pi 5 8GB successfully.

## Prepare the host

Please setup VisualStudio Code and Docker as described in [Setup](setup.md).

## Prepare the dev container

The pre-built dev container is only available for amd64 hosts,
so first the container needs to be build locally on arm64.
First clone the EB corbos linux dev container repository from https://github.com/Elektrobit/ebcl_dev_container.
Then build the container for arm64 by running the _builder/build_container_ script.

## Prepare the workspace

Next you need the EB corbos Linux template workspace.
Clone the template git repository from https://github.com/Elektrobit/ebcl_template.
Then open Visual Studio Code and install the dev container extension.
Open the workspace file _ebcl_sdk.code-workspace_.
Press the "Reopen in container" button of the popup
or open the VS code shell by pressing _Ctrl + Shift + P_
and select the "Reopen in container" command.

## Build an arm64 image

Now you can build arm64 images.
Open the folder containing the image description you want to build,
e.g. _/workspace/images/arm64/qemu/ebcl/crinit/debootstrap_,
in the integrated terminal in the dev container.
Then run `make` to build the image.
The build results are stored in a new created _build_ subfolder.
In case of QEMU images, the QEMU VM will be started automatically.

## Cross-building

Cross building is supported when the host allows execution of binaries of the target architecture.
To allow executing binaries for different architectures, install _binfmt_ support.
On Ubuntu, you can install it by running: `sudo apt install binfmt-support qemu qemu-user-static`.

Then you can build the image in the same was as the arm64 images.
Open the image folder in the terminal in the dev container,
e.g. _/workspace/images/amd64/qemu/ebcl/crinit/debootstrap_.
Then run the image build by executing `make` in the folder.
