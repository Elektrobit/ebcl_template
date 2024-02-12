# User Guide
This document describes the creation and start of an SDK docker container 
which supports building an application based on EB corbos Linux (EBcL) 
as well as the starting of a qemu image running the EBcL for x86_64 based on crinit.

After installation and run of this application there can be called a script which is collecting some report data used for certification.

## Setup development environment
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
To build an EBcL image there are two scripts available for amd64 and aarch64 architecture. 
```bash
box_build_image.sh <image description>
cross_build_image.sh <image description>
```
The image binary files and log files are stored at the folder **result_image/<image_name>**.

For more information about creating EBcL images are available in the official EBcL user guide.

## Build sysroot
Before building applications a sysroot needs to be created. 
```bash
box_build_sysroot.sh <image description>
cross_build_sysroot.sh <image description>
```

## Building demo application
### Note
The following step-by-step guide provides an example how building an application can look like.
As there are many different options available to build an application this example will not fit to all possible options.

The example consits of a small "Hello World"-C++ application called **myjsonapp** using json-cpp as an additional library.
The result of the example is a Debian package which is added directly to the target image.
The target image used for this example is **qemu-crinit-amd64**.
### Step 1: Create sysroot
To create the sysroot the script **box_build_sysroot.sh** is used by executing the command
```bash
box_build_sysroot.sh /build/workspace/images/qemu-crinit-amd64/appliance_sysroot.kiwi
```
in a terminal inside the Docker container.
### Step 2: Build application and create Debian package
To build the demo application copy the content of **/build/workspace/demo/myjsonapp** to **/build/app**.
Then run the following commands in a terminal inside the SDK Docker container:
```bash
prepare_deb_metadata.sh
build_package.sh
gen_sign_key.sh
source /build/scripts/env.sh
prepare_repo_config.sh
```
The generated output files are stored at the folders **/build/result_app** and **/tmp/myjsonapp**.

### Step 3: Build the target image
After building the Debian package can be added to the target image.

As the Debian package is not part of any official repository it is needed to host a temporary local repository.
To do this the script **serve_packages.sh** can be used which start hosting the local repository. 
To not block the terminal the execution can be started as background task by executing the following line in a terminal inside the SDK Docker container:
```bash
serve_packages.sh &
```
**_NOTE:_**  Do not terminate the script or terminal session until the target image is built!

To add the built Debian package the following line needs to be added to /build/workspace/images/qemu-crinit-amd64/appliance_sysroot.kiwi in section **packages type="image"**:
```bash
<package name="my-json-app"/>
```

Next step is to build the image by executing the script box_build_sysroot.sh in a terminal inside the SDK Docker container.
```bash
box_build_sysroot.sh /build/workspace/images/qemu-crinit-amd64/appliance_sysroot.kiwi
```
The result will be stored in /build/result_image/qemu-crinit-amd64. The image itself is the file qemu_crinit_amd64.x86_64-1.1.0-0.qcow2.

### Step 4: Start the target image
In order to start the target image in QEMU run the following command in a terminal inside the SDK Docker container:
```bash
/build/workspace/images/run_qemu_x86_64.sh \
/build/result_image/qemu_crinit_amd64/qemu_crinit_amd64.x86_64-1.1.0-0.qcow2
```

**_NOTE:_** The target image can be stopped by running the command
```bash
crinit-ctl poweroff
```

### Step 5: Run application
#### crinit
The used image for this example using crinit as init daemon.
Every application which shall be controlled by crinit needs a task configuration file (stored in /etc/crinit/crinit.d/).
More information about crinit can be found at https://github.com/Elektrobit/crinit.
This example already have a task configuration file as part of the Debian package, therefore no action needed here.

#### Verify application start 
In order to verify the status of the application(s) run the command
```bash
crinit-ctl list
```
The status of the example application shall be **running** or **stopped** (in case application has already been finished).

## Certification data
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
