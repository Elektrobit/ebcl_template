## EBcL initrd generator

Tool to create custom inittial RAM disk (initrd) based on busybox using YAML configuration file.

It parses the configuration, installs BusyBox, downloads and extracts kernel modules debian packages, adds device nodes, copies files, creates an init script, and finally, creates the initrd image.

## Reads Configuration

Parses a YAML configuration file to obtain necessary parameters like kernel modules, root device, device nodes, files to include and kernel version.

## Installs BusyBox

Downloads the BusyBox debian package, extracts it, and copies the BusyBox binary to the initrd image, setting up the necessary symlinks.

## Downloads and Extracts Debian Packages

Downloads debian packages containing kernel modules, extracts the specified modules, and includes them in the initrd image.

## Adds Device Nodes

Creates necessary device nodes in the `/dev` directory of the initrd image based on the configuration.

## Copies Files

Copies specified files and directories from the host system to the initrd image, setting the appropriate permissions.

## Creates Init Script

Generates an init script that initializes the system, loads kernel modules, mounts the root filesystem, and switches to the new root.

## Creates Initrd Image

Uses the `cpio` command to create the initrd image from the files and directories set up in a temporary directory.

## Usage
create_initrd.py <config.yaml> <output_directory>
