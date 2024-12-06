As described in the previous chapters, a EB corbos Linux image typically consists of a _Makefile_ and specification yaml files.
The _Makefile_ is SoC specific, should be only changed during SoC and board bring-up, and can be shared with all images for the SoC.
If different image variants are used, also parts of the image configuration can be shared.
To avoid redundancy, the example images make use of this sharing.
The example images are contained in the _images_ folder of the EB corbos Linux template workspace, and are structured by CPU architecture, distribution, init-manager and further variant descriptions.
The example image for amd64 and the QEMU target, using the EBcL distribution, and the crinit init-manager is contained in _images/amd64/qemu/ebcl/crinit_, and you can build and run it by executing `make` in this folder.

Please be aware that the example images are only considered for educational purposes.
These images are not pre-qualified.
If you are an EB corbos Linux customer, and want to start a new industrial embedded Linux project which requires qualification and maintenance, please choose one of the provided _reference images_ as a starting point.
These images are already pre-qualified and get up to 15 years of maintenance.
