# Root generator

A root tarball can be generated with the root generator.

**root_generator** — Built a root tarball

## Description

Creates a custom, root tarball using YAML configuration file. It can be used for example to build a normal rootfs, but also the build chroot build environments containing tooling needed for building other artifacts. The synopsis is `root_generator <root>.yaml <output_path> --no-config --sysroot`

![BuildTools](../assets/root_generator.drawio.png)

The internal steps are:

 1. Read in YAML configuration file
 2. If sysroot is configured add generic sysroot packages like g++
 3. Depending on the configuration build the image with kiwi or elbe
 4. If configuration is not skipped run config.sh script if present
 5. Copy image tar to output folder

## Configuration

### Parameters

**--no-config, -n**: Skip the root filesystem configuration step

**--sysroot, -s**: Build a sysroot insteas of a normal root tarball

### Yaml file

Potential configuration parameters are documented in the section "Configuration parameters" and examples are given in the section "The example images"
