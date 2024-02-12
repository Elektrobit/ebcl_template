# User Guide
This document describes the creation and start of an SDK docker container 
which supports building an application based on EB corbos Linux (EBcL) 
as well as the starting of a qemu image running the EBcL for amd64 or aarch64 architecture based on init system (crinit or systemd).

After installation and run of this application there can be called a script which is collecting some report data used for product compatibility testing.

## Preconditions
### Download EB corbos Linux SDK workspace
Download the EB corbos Linux SDK workspace which is published in the Elektrobit Github organization
as a template repository (https://github.com/Elektrobit/ebcl_template/) at branch **PSS/main** by running the command
```bash
git clone https://github.com/Elektrobit/ebcl_template.git -b PSS/main
```

### Tools required locally
As prerequisites, you need to have the following tools set up:

- VS Code (https://code.visualstudio.com/)

- The VS Code Dev Containers extension set up according to the instructions at https://code.visualstudio.com/docs/devcontainers/containers.

## Create and start SDK docker container
This section describes the steps for creating and starting an SDK docker container which supports building an application based on EB corbos Linux (EBcL).

### Build and start SDK docker container
Start VS Code.

If the EB corbos Linux SDK workspace has been downloaded to a remote server open a remote connection to this server.

Open the workspace **/home/ubuntu/EBcL/ebcl_sdk_1-0-0.code-workspace**.

Select **Reopen in Container** when being asked for.

To pull an updated version of the container image and update your local container, use the command **Dev Containers: Rebuild Without Cache and Reopen in Container** (press Ctrl + Shift + P in order to get the command menu).

Then there is built and started the SDK docker container.

For the following steps there have to be opened new terminals inside VS Code where the related commands have to be entered.

## Build EBcL image
In order to build an EBcL qemu image based on init system (crinit or systemd) run the following commands at a terminal opened at the SDK (referred as SDK terminal):

- Architecture amd64
```bash
box_build_image.sh workspace/images/qemu-<crinit or systemd>-amd64/appliance.kiwi
box_build_sysroot.sh workspace/images/qemu-<crinit or systemd>-amd64/appliance_sysroot.kiwi
```
- Architecture aarch64
```bash
cross_build_image.sh workspace/images/qemu-<crinit or systemd>-aarch64/appliance.kiwi
cross_build_sysroot.sh workspace/images/qemu-<crinit or systemd>-aarch64/appliance_sysroot.kiwi
```

The image binary files and log files are stored at the folder **result_image/ebcl_qemu_\<crinit or systemd\>_\<amd64 or aarch64\>**.

## Build application
### Get all application sources needed for building the application
In this step all application sources needed for building the application have to be made available inside the SDK docker container.

Note that there have to be configured the related files at **/etc/apt/sources.list.d/** if the sources have to be retrieved via apt-get.

The application sources have to be stored at the folder **app**.

### Build application
Adapt the variables **APP_NAME** and **APP_VERSION** in the file **workspace/gpg-keys/env.sh** for your application.

Then run the following commands at the SDK terminal:

- Architecture amd64
```bash
prepare_deb_metadata.sh
build_package.sh
gen_sign_key.sh
source /build/scripts/env.sh
prepare_repo_config.sh
serve_packages.sh&
```
- Architecture aarch64
```bash
prepare_deb_metadata.sh
cross_build_package.sh
gen_sign_key.sh
source /build/scripts/env.sh
prepare_repo_config.sh
serve_packages.sh&
```

The generated output files are stored at the folders **result_app** and **/tmp/\<your application\>**.

### Configure application and rebuild image
Add your application package at the file **workspace/images/qemu-\<crinit or systemd\>-\<amd64 or aarch64\>/appliance.kiwi** depending on the used init system and architecture by adding the line
```bash
        <package name="<your application>"/> 
```
at the section **\<packages type="image"\>** with **\<your application\>** set to the value provided as **APP_NAME**.

Then build the image including your application by running the following command at the SDK terminal:

- Architecture amd64
```bash
box_build_image.sh workspace/images/qemu-<crinit or systemd>-amd64/appliance.kiwi
```
- Architecture aarch64
```bash
cross_build_image.sh workspace/images/qemu-<crinit or systemd>-aarch64/appliance.kiwi
```

## Start EBcL qemu image
In order to start the EBcL image run the following command at a new terminal opened at the SDK (referred as target terminal):

- Architecture amd64
```bash
workspace/images/run_qemu_x86_64.sh result_image/qemu_<crinit or systemd>_amd64/qemu_<crinit or systemd>_amd64.x86_64-1.1.0-0.qcow2
```
- Architecture aarch64
```bash
workspace/images/run_qemu_aarch64.sh result_image/qemu_<crinit or systemd>_aarch64/qemu_<crinit or systemd>_aarch64.aarch64-1.1.0-0.qcow2
```

Note that the target can be stopped by running the command

- crinit image
```bash
crinit-ctl poweroff
```
- systemd image
```bash
systemctl poweroff
```

## Run application
### Verify application start
At the target terminal ensure that the related init task configuration files are stored at destination directory 
(**/etc/crinit/crinit.d/** for crinit system and **/lib/systemd/system/** for systemd system).

In order to verify the status of the application(s) run the command

- crinit image
```bash
crinit-ctl list
```
- systemd image
```bash
systemctl status
```

If the status is running (or done for applications finished already successfully) all the required tests can be executed.

Note that in case of systemd this information can be retrieved for an \<application\> using the command
```bash
systemctl status <application>
```


### System call information
In order to provide system call information of your application run the following command at the target terminal:
```bash
strace -qcf /usr/bin/<application name> 1>/tmp/<application name> 2>/tmp/<application name>_strace&
```
where \<application name\> corresponds with the binary file of the application.

If available this information is included at the report described below.

Note that the application started with the strace call above has to be finished in order to provide the related output in the files given at the command.

## Get report
### Run collect report script
From the SDK terminal copy the collect report script to the target:
```bash
scp -P 2222 workspace/images/collect_report.sh root@127.0.0.1:/etc/
```

At the target terminal run the collect report script
```bash
/etc/collect_report.sh -bf <binary file of application>
```
with the absolute path of the binary file of the application.

For retrieving the description of this script please call
```bash
/etc/collect_report.sh --help
```

This script is generating an archive file
```bash
/<application name>_report.tar.gz
```
where \<application name\> corresponds with the given name of \<binary file of application\>.

### Get report archive
Get the report archive file at the SDK terminal by running the command
```bash
scp -P 2222 root@127.0.0.1:/<application name>_report.tar.gz .
```

For the certification please provide this report archive file.

## Demo application
There are provided the demo applications **hello-world** and **myjsonapp** located at the sub-folder **workspace/demo**.

### Copy demo application
There is provided a script that copies the required files of the selected demo application 
from the related sub-folder at folder **workspace/demo** to the folder **app**.

At SDK terminal run the command 
```bash
workspace/images/copy_demo_app.sh -da <demo application> -as <application start>
```
where \<demo application\> is the name of the demo application and
\<application start\> indicates the type of starting the application.

For \<application start\> the following values are supported:

- **manual**

  The demo application is not started automatically by the init system and has to be started manually.

- **crinit**

  The demo application is started automatically by the init system **crinit**.

- **systemd**

  The demo application is started automatically by the init system **systemd**.

Note that the last two options require that the EBcL image has been built for the same init system.

For retrieving the description of this script please call
```bash
workspace/images/copy_demo_app.sh --help
```

### Build demo application

Follow the steps mentioned above at build application for the selected demo application.

### Run demo application
Follow the steps mentioned above at run application and get report for the selected demo application.

Note that the binary files created at target are:

- **/usr/bin/hello-world** for demo application **hello-world**

- **/usr/bin/MyJsonApp** for demo application **myjsonapp**
