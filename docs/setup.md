# Setup

The EB corbos Linux SDK is tested with Ubuntu 22.04 and Ubuntu 24.04 host environments on x86_64 machines. It is not compatible with ARM hosts, but ARM host support is planned.

The build host needs to provide a Docker installation and a Python 3 installation, and Docker needs support for running privileged containers. For x86_64 images KVM acceleration can be used for speeding up the build, if nested virtualization is supported in the host environment.

The SDK contains a [modified variant of elbe](https://github.com/Elektrobit/elbe), which allows image building without using a nested virtual machine. This simplifies the setup and provides good build speed, but it requires support for executing non-native binaries if images for foreign architectures shall be built. To make this work, the host needs to support _binfmt_. On Ubuntu hosts, _binfmt_ can be enabled by installing the packages _binfmt-support_ and _qemu-user-static_. To allow mount operations which are required during image build, a privileged execution of the container is necessary, and the _/dev_ folder needs to be bind-mounted into the container to allow access to newly created _losetup_ devices. Running other workloads on the build host may cause issues, since _binfmt_ and _losetup_ configure the kernel and therefore modify the host environment for all running processes.

The following sections assume that you don't have an Ubuntu 22.04 or 24.04 host OS and use the Remote SSH feature of Visual Studio Code to connect to a remote environment as build host. This will work if you can SSH into the build host and doesn't require UI-support. On Windows, WSL2 should also work.

## Optional: Prepare Virtual Box VM

If you don't have already an Ubuntu development host, you can setup a new one using [VirtualBox](https://www.virtualbox.org/), a free hypervisor available for many operating systems.

First download an Ubuntu ISO image. For preparing this section, I used an Ubuntu 24.04 server ISO, since a desktop UI is not needed.

First download and install [VirtualBox](https://www.virtualbox.org/), then create a new virtual machine with the following options:

- RAM: 8192 MB (less should also work)
- CPU: 3 cores (more is better, less will also work)
- Disc: 100 GB (more is better, less will also work)
- A second, host-only network interface.

Skipping automatic installation will allow you to change the hardware settings before the installation, if you add the second interface after installation, you must configure it manually.

Boot the VM with the Ubuntu ISO image and follow the installation wizard. I have chosen the minimal server variant.

After installation, log in to the VM and install openssh-server, docker and git: `sudo apt install openssh-server docker.io git`.
Get the IP address of the VM by running the command `ip addr`. The address starting with `192.168.` is the one of the host-only interface.
For me the address was `192.168.56.106`.

## Setup Visual Studio Code

Install [Visual Studio Code](https://code.visualstudio.com/) on your local machine. It's for free available for all major operating systems.

Run [Visual Studio Code](https://code.visualstudio.com/) (VS Code) and open the extensions view (_CTRL_ + _SHIFT_ + _X_).
Now install the _Remote SSH_ and the _Dev Containers_ extensions.

### Prepare SSH connection

Let's try to connect to the Ubuntu remote development host. Open a new terminal in VS Code and type `ssh <your user>@<IP of the host>`.
In my case it is: `ssh ebcl@192.168.56.106`.
If it works, you are asked to accept the key, then you can login with your password.
This will give you a shell on the remote development host.

If you are on Windows, and you get an error that ssh is not available, you can install [git for windows](https://www.git-scm.com/download/win).
This will also give you a ssh client.

To avoid typing your password all the time, you can authenticate with a key.
To use key authentication, disconnect form the remote host by typing `exit`, and then run `ssh-copy-id <your user>@<IP of the host>` in the VS Code shell.
If you are on Windows and get the error that the command `ssh-copy-id` is not known, you can use `type $env:USERPROFILE\.ssh\id_rsa.pub | ssh <your user>@<IP of the host> "cat >> .ssh/authorized_keys"`. If you don't have an SSH authentication key, you can create one using the `ssh-keygen` command.

### Connect using VS Code _Remote SSH_ plugin

Now you are ready to use the _Remote SSH_. Open VS Code, then open the command palette (_Ctrl_ + _Shift_ + _P_) and choose _Remote SSH: Connect to host_.
Select _Add new host_  and enter `<your user>@<IP of the host>`. In my case, I entered `ebcl@192.168.56.106`. Then select Linux as host OS.
VS Code will install the remote VS Code server on the remote host, and open a window connected to this server.
If it works, you should see `SSH: <IP of the host>` in the lower left corner. Pressing on this element will bring up the connection menu.

### Install required tools and clone ebcl_template repository

To use the SDK, we need _git_ to clone the remote repository (or you download it otherwise), and we need _Docker_ to run the dev container.
All other required tools come as part of the container.

When connect to the remote host, opening a new terminal in VS Code will give you a shell on the remote machine.
Use this shell to install _Docker_ and _git_: `sudo apt install docker.io git`.
To be able to use the docker service, your user needs to be part of the docker group.
Add your user to this group by running `sudo usermod -aG docker $USER`.
This needs a restart of the remote development host to take an effect. To restart the host, run `sudo reboot`.
This will disconnect your VS Code remote connection, and you need to reconnect after restart of the remote development host.

Open again a shell on the remote machine, change you your preferred storage location, and clone the _ebcl_template_ repositoy
by running: `git clone https://github.com/Elektrobit/ebcl_template.git`. This will give you a new folder _ebcl_template_.

To build the container, change to _ebcl_template/container_ and run `./build_container`.
This will build the free version of the SDK container. Wait for the build to finish, this may take a while for the first run.
If you got an official EB corbos Linux delivery or evaluation bundle, this contains a pre-build container which may contain
additional proprietary tools, e.g. a safety certified compiler. In this case, please follow the instruction in the delivery
document to import the pre-built container.

Now you are ready to start development!

### Using the EBcL SDK VS Code integration

To use VS Code for developing with the EBcL SDK, choose _File > Open Workspace from File_ and navigate to the ebcl_template location.
Select the _ebcl_sdk_1-2.code-workspace_ file. This will open the folder bind-mounted in the docker dev container environment.

Now you can use the VS Code build tasks (_Ctrl_ + _Shift_ + _B_) to build the example images and build and package the example apps.

### Using the EBcL SDK container stand-alone.

To use the EBcL SDK container standalone, you can run and enter the container for interactive mode using the _run_container_ script.
If you don't provide any arguments, this will drop you to an interactive shell. If you provide arguments, this will execute the command
given as argument in the container.

If you want to integrate the container in a CI environment, or another IDE, take a look at the _run_container_ script.

If you want to use _pbuilder_ for application packaging, image builds with _elbe_, or KVM accelerated image builds with _kiwi-ng_,
you need to run the container as privileged container.

For _elbe_ image builds, you also need to bind-mount the `/dev` folder form the host into the container, to make new created
_losetup_ devices available.

The tooling in the container expects the VS Code workspace bind-mounted at `/workspace`, but this is only used for some edge cases
which manipulate the static considered parts of the build environment. Most of the commands make use of the mountpoints below the 
`/build` folder.

All build results will be written to sub-folders of `/build/results`. In stand-alone mode, a host folder should be rw bind-mounted
to this location.

The users identity, i.e. used for package maintainer information, is taken from the _env_ script at `/build/identity/env`, located
at `/identity/env` in the template. This folder can be mounted read-only, to avoid unintended change of the identity information.

The image descriptions are expected to be located at `/build/images`. This folder should also be bind-mounted read-only to ensure that
the image descriptions are not affected as a side effect of SDK commands. The container environment automatically overlay-mounts this
folder writeable at the location `/tmp/build/images`.

The sysroots should also be read-only bind-mounted, to ensure that the application build process cannot manipulate it and provide repeatable
results. The SDK cmake commands expects the sysroot at the locations `/build/sysroot_x86_64` and `/build/sysroot_aarch64`.

### Enabling nested virtualization for KVM support

The Linux KVM technology allows running virtual machines, for the same CPU architecture as the host, with almost native speed.

To make use of this in VirtualBox, you need to disable the Windows Hypervisor.
Please be aware that this may affect other virtualization tooling like Windows WSL.
To disable the Windows Hypervisor, open a PowerShell as Administrator, and run `bcdedit /set hypervisorlaunchtype off`.
Afterwards, you need to reboot your Windows machine.

After the reboot, you can enable nested virtualization for your VirtualBox VM by editing the machine, choosing _System > CPU_
and enabling the checkbox for nested VT-x/AMD-V.
