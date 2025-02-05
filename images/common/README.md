# Common configuration

This folder contains the common configuration for all example images.

## Structure

The less general configuration is structured as child folders.

Example for the QEMU amd64 root filesystem using the crinit init manager:
The used file is _amd64/crinit/root.yaml_.
The folder _amd64/crinit_ contains the amd64 specific configuration for the crinit init manager.
If there would be also QEMU specific configuration needed, then the folder would be _qemu/amd64/crinit_.
The _amd64/crinit/root.yaml_ includes _crinit/root.yaml_, which adds the architecture independent configuration for the crinit init manager.
The _crinit/root.yaml_ includes _root.yaml_, which adds the init manager independent packages.

The order of the folders is SoC, CPU architecture, init manager, other.
