# EB corbos Linux Images

As described in the previous chapters, a EB corbos Linux image typically consists of a _Taskfile_ and specification yaml files.
The build steps for different SoCs have many similarities, and generic build steps are provided as template tasks in _images/tasks_.
This folder also contains central image build descriptions for QEMU, Raspberry Pi and NXP RDB2, to minimize the redundancy between the image taskfiles.

The example images are contained in the _images_ folder of the EB corbos Linux template workspace,
and are structured by CPU architecture, distribution and further variant descriptions.
The example image for arm64 and the QEMU target, using the 1.x line of the EBcL distribution
is contained in _images/arm64/qemu/ebcl_1.x_,
and you can build and run it by executing `task` in this folder.

The runtime configuration of Linux is highly independent form the hardware,
and the final runtime configuration of the different images is very similar.
To avoid redundancy, most aspects of the image descriptions are centralized in _images/common_.
For more details about the structuring of this configuration, take a look at the _README.md_ contained in the folder.

Please be aware that the example images are only considered for educational purposes.
These images are not pre-qualified and provide a userland for interactive usage and exploration.
If you are an EB corbos Linux customer, and want to start a new industrial embedded Linux project
which requires qualification and maintenance, please choose one of the provided _reference images_ as a starting point.
These images provide a minimized userland, are already pre-qualified and get up to 15 years of maintenance.
