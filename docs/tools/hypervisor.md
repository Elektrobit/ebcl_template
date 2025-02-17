# Hypervisor Configurator

Creates a configuration for the hypervisor

## Description

The hypervisor configuration is a rather complex topic.
This tool enables configuring the hypervisor using yaml files to describe the VMs, hardware configuration, shared memory configuration and more.

To generate a configuration the tool uses a set of files:

 * A configuration schema that describes the yaml configuration model (_schema.yaml_)
 * A python model of that schema to allow postprocessing of the loaded configuration (_model.py_)
 * A set of templates to generate the configuration from

A basic set of these files that should fit all versions of the hypervisor is delivered with the toolchain.
Additionally a directory containing specialization for the files can be passed to the hypervisor.
This specialization should be bundled together with the hypervisor version used.
It allows adding features to the configurator based on the hypervisor version used.
