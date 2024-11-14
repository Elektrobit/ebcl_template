# Setup

The EB corbos Linux template workspace is tested using Ubuntu 22.04 and Ubuntu 24.04 host environments on x86_64 machines.
It is not compatible with other host CPU architectures, but arm64 host support is planned for a future release.

The build host needs to provide a Docker installation and a Python 3 installation, including Python3 venv.
Docker needs support for running privileged containers.

The EB corbos Linux template workspace is based on a [dev container](https://github.com/Elektrobit/ebcl_dev_container), and is not using VMs for cross-building.
This simplifies the setup and provides good build speed, but it requires support for executing non-native binaries if images for foreign architectures shall be built.
To make this work, the host needs to support _binfmt_. On Ubuntu hosts, _binfmt_ can be enabled by installing the packages _binfmt-support_ and _qemu-user-static_. To allow mount operations which are required during image build, a privileged execution of the container is necessary, and the _/dev_ folder needs to be bind-mounted into the container to allow access to newly created _losetup_ devices.
Running other workloads on the build host may cause issues, since _binfmt_ and _losetup_ configure the kernel and therefore modify the host environment for all running processes and containers.

The following sections assume that you don't have an Ubuntu 22.04 or 24.04 host OS and use the Remote SSH feature of Visual Studio Code to connect to a remote environment as build host.
This will work if you can SSH into the build host and doesn't require UI-support on the build host.
On Windows, WSL2 should also work.

## Optional: Prepare Virtual Box VM

If you don't already have an Ubuntu development host, you can create a new one using [VirtualBox](https://www.virtualbox.org/), a free hypervisor available for many operating systems.

First download an Ubuntu ISO image.
For preparing this section, I used an Ubuntu 24.04 server ISO, since a desktop UI is not needed.
Then download and install [VirtualBox](https://www.virtualbox.org/), and create a new virtual machine with the following options:

- RAM: 8192 MB (less should also work)
- CPU: 3 cores (more is better, less will also work)
- Disc: 100 GB (more is better, less will also work)
- A second, host-only network interface.

Skipping automatic installation will allow you to change the hardware settings before the installation, if you add the second interface after installation, you must configure it manually.

Boot the VM with the Ubuntu ISO image and follow the installation wizard.
I have chosen the minimal server variant.

After installation, log in to the VM and install openssh-server, docker and git: `sudo apt install openssh-server docker.io git`. Get the IP address of the VM by running the command `ip addr`. The address starting with `192.168.` is the one of the host-only interface.
For me, the address was `192.168.56.106`.

### Enabling nested virtualization for KVM support

The Linux KVM technology allows running virtual machines, for the same CPU architecture as the host, with almost native speed.
To make use of this in VirtualBox, you need to disable the Windows Hypervisor.
Please be aware that this may affect other virtualization tooling like Windows WSL.
To disable the Windows Hypervisor, open a PowerShell as Administrator, and run `bcdedit /set hypervisorlaunchtype off`. Afterwards, you need to reboot your Windows machine.

After the reboot, you can enable nested virtualization for your VirtualBox VM by editing the machine, choosing _System > CPU_ and enabling the checkbox for nested VT-x/AMD-V.

## Setup Visual Studio Code

Install [Visual Studio Code](https://code.visualstudio.com/) on your local machine.
It's available for free for all major operating systems.

Run [Visual Studio Code](https://code.visualstudio.com/) (VS Code) and open the extensions view (_CTRL_ + _SHIFT_ + _X_). Now install the _Remote SSH_ and the _Dev Containers_ extensions.

If you will not use an remote development host you can skip the next two sections and start with installing the required tools.

### Prepare SSH connection

Let's try to connect to the Ubuntu remote development host.
Open a new terminal in VS Code and type `ssh <your user>@<IP of the host>`. In my case it is: `ssh ebcl@192.168.56.106`. If it works, you are asked to accept the key, then you can login with your password.
This will give you a shell on the remote development host.

If you are on Windows, and you get an error that ssh is not available, you can install [git for windows](https://www.git-scm.com/download/win). This will also give you a ssh client.

To avoid typing your password all the time, you can authenticate with a key.
To use key authentication, disconnect from the remote host by typing `exit`, and then run `ssh-copy-id <your user>@<IP of the host>` in the VS Code shell.
If you are on Windows and get the error that the command `ssh-copy-id` is not known, you can use `type $env:USERPROFILE\.ssh\id_rsa.pub | ssh <your user>@<IP of the host> "cat >> .ssh/authorized_keys"`. If you don't have an SSH authentication key, you can create one using the `ssh-keygen` command.

### Connect using VS Code _Remote SSH_ plugin

Now you are ready to use the _Remote SSH_. Open VS Code, then open the command palette (_Ctrl_ + _Shift_ + _P_) and choose _Remote SSH: Connect to host_. Select _Add new host_  and enter `<your user>@<IP of the host>`. In my case, I entered `ebcl@192.168.56.106`. Then select Linux as the host OS.
VS Code will install the remote VS Code server on the remote host, and open a window connected to this server.
If it works, you should see `SSH: <IP of the host>` in the lower left corner.
Pressing on this element will bring up the connection menu.

### Install required tools and clone ebcl_template repository


If you start from a plain Ubuntu 22.04 installation, you can install the needed dependencies using the following command: `sudo apt install docker.io python3 python3-venv python-is-python3 binfmt-support qemu-user-static`

To use dev containers, your user (on the remote machine) needs to be able to create local Docker containers.
To give your user these rights, you need to add the user to the docker group with the command: `sudo usermod -aG docker $USER`. The changes become active after a new login.
Close the remote connection using the menu in the lower left corner of your VS Code window and reopen the connection using the command palette or if not using a remote machine simply log out and in again.

To use the SDK, we need _git_ to clone the remote repository (or you download it otherwise), and we need _Docker_ to run the dev container.
All other required tools come as part of the container.

Open again a shell on the remote machine, change you your preferred storage location, and clone the _ebcl_template_ repository by running: `git clone https://github.com/Elektrobit/ebcl_template.git`. This will give you a new folder _ebcl_template_.

In VS Code, open “File > Open Workspace from File…”, navigate to the _ebcl_template_ folder and select _ebcl_sdk.code-workspace_. Now you can enter the dev container by opening the remote menu in the lower left corner and selecting “Reopen in Container”.
This will automatically run a local build of the EB corbos Linux dev container.
The first time, when the container is built completely from scratch, may take quite some time.
On my machine it takes about 30 minutes.
When you open the workspace a second time, it will be a matter of seconds.

Now you are ready to start development!

### Using the EBcL SDK VS Code integration

To use VS Code for developing with the EBcL SDK, choose _File > Open Workspace from File_ and navigate to the ebcl_template location.
Select the _ebcl_sdk.code-workspace_ file.
This will open the folder bind-mounted in the docker dev container environment.

Now you can use the VS Code build tasks (_Ctrl_ + _Shift_ + _B_) to build the example images and build and package the example applications.

### Using the EBcL SDK container stand-alone.

If you don’t want to use VS Code, or you want to integrate the EBcL SDK in your CI workflows, you can use the dev container stand-alone.
For more details on how to do this, take a look at [dev container](https://github.com/Elektrobit/ebcl_dev_container).

