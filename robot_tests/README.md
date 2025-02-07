# EB corbos Linux robot test integration and library

EB corbos Linux provides a Robot test integration which allows
automated testing of image builds and QEMU images.
To allow running the same Robot tests for multiple images,
and to allow test case specific QEMU parameters, a helper script
and a environment variable interface is used.


## Environment variable interface

### Test framework environment configuration

- EBCL_TF_BUILD_MODE: Selection of image build interface, see _lib/Image.py_.

- EBCL_TF_IMAGE_BASE: Image description base folder, e.g. /workspace/images, see also EBCL_TC_IMAGE.

- EBCL_TF_CLEAR_CMD

### Test suite specific parameters

- EBCL_TC_IMAGE: Image descrption path form base folder, e.g. arm64/qemu/jammy.
  The folder where the build command is executed is ${EBCL_TF_IMAGE_BASE}/${EBCL_TC_IMAGE}.

- EBCL_TC_ROBOT_FILES: Name of the robot files which include the tests to be executed,
  e.g. "docker crinit" to run tests from the _docker.robot_ and _crinit.robot_ for the image
  defined by ${EBCL_TF_IMAGE_BASE}/${EBCL_TC_IMAGE}.

- EBCL_TC_SHUTDOWN_COMMAND: Command used to shutdown the image,
  e.g. _systemctl poweroff_ for systemd or _crinit poweroff_ for crinit.

- EBCL_TC_SHUTDOWN_TARGET: Wait search term for image shutdown completed.
