# Developing apps
The workspace provides two simple applications to explain the development workflow and interactions with the operating system.

 <!--- EXPLAIN BOTH APPS HERE! -->

For applications development, interaction with different target types is handled via a set of predefined, generic, Visual Studio Code tasks.
Currently, the example workspace provides four different CMake presets for building, corresponding to four possible deployment targets.
The supported presets are the following:

|Preset|Arch|Sysroot|Image|
|------|----|-------|-----|
|qemu-x86_64|x86_64|sysroot_x86_64|/workspace/images/amd64/appdev/qemu/[crinit\|systemd]|
|qemu-aarch64|aarch64|sysroot_aarch64|/workspace/images/arm64/appdev/qemu/[crinit\|systemd]|
|hardware|aarch64|sysroot_aarch64|/workspace/images/arm64/appdev/[rdb2\|pi4]/[crinit\|systemd]|

The different columns represent the name of the preset, CPU architecture, the sysroot the application is built against and a path to a possible image configuration with either crinit or systemd as init daemon.

For each preset a configuration entry in `/workspace/apps/common/deployment.targets` is present, defining target address, ssh settings and user credentials as well as the gdb port used for debugging.
Target access via ssh is based on the `TARGET_IP`, `SSH_USER`, `SSH_PORT` and `SSH_PREFIX`.
In the current example configurations for remote targets, the `SSH_PREFIX` is used to handover the login password via `sshpass -p {password}`.

## Build, execute and debug demo applications

The following section explains how to build, execute and debug the included example applications.
All required steps are handled by Visual Studio Code tasks.
Some of the mentioned tasks will reference an "active build preset".
This means that Visual Studio code will determine the application for which the task will be executed for.
For this mechanism to work properly make sure, that the focused editor window shows a file of the application you want the task to run for.
This file may belong to the application folder or any of its subfolders.

### Build

Before you can build any of the example applications, please make sure to run `make sysroot_install` for the used image configuration.
As an example, for the amd64 qemu image with crinit as init daemon, building the sysroot would be done like this:

```{bash}
cd /workspace/images/amd64/appdev/qemu/crinit
make sysroot_install
```

In order to build the applications, use the Visual Studio Code CMake extension on the Visual Studio Code bottom ribbon:

* Choose active project as `my-json-app` or `meminfo-reader`
* Choose active configure preset `qemu-x86_64`, `qemu-aarch64` or `hardware`
* Click on `Build`

Alternatively to the use of Visual Studio Code tasks, building can also be done directly via cmake.
The following commands will configure, build and install the `my-json-app` for the `qemu-x86_64` preset.

```{bash}
cd /workspace/apps/my-json-app/
cmake . --preset qemu-x86_64
cmake --build --preset qemu-x86_64
```

After building is done, the artifacts will be available in `/build/results/apps/{application}/{preset}/build/install/`.

### Pre-execute steps

Before you can start the application for any of the available presets, you need to start the corresponding image.
Again, we take the amd64 qemu crinit image as example.
The following command will start the qemu instance, as well as builds the image beforehand if needed:

```{bash}
cd /workspace/images/amd64/appdev/qemu/crinit
make
```

Afterwards, you can run task `Deploy app from active build preset` to deploy the required artifacts for the currently active build preset.

### Run demo applications

The applications can be started with the task `Run app from active build preset`.
Based on the build preset, the ssh connection parameters are derived from `/workspace/apps/common/deployment.targets` and the application is called on the target via an ssh session.
All output messages of the application, will be displayed in a terminal window associated to the used run task.
Alternatively, you could also login via ssh to the target and call the application from there directly.

### Post-execute steps

This step is not required for the provided example applications, since both terminate directly and don't include any continuous loops.
Nevertheless, your own applications, may behave differently.
In order to stop the execution of an application you can either press CTRL-C in the corresponding terminal window or stop the parent task.
To stop the parent task click on the Stop icon in the task `Run app from active build preset` to stop the application.

### Debugging demo applications

Visual Studio Code can be used as a gdb frontend for debugging.
In order to debug the application from the current active preset press "F5".
Before Visual Studio Code starts the gdb and after debugging, the following tasks are executed automatically.

Pre debug:

* Build and check target connection
* Trigger incremental application build
* Perform ssh connection test and update ssh keys, if needed
* Build and check target connection
* Update application deployment
* Prepare application specific gdbinit file
* Start gdbserver on remote target

Post debug:

* Stop gdbserver on remote target
