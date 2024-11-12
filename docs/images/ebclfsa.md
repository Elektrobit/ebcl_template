# Building an EB corbos Linux for Safety Applications image

Building the image for ebclfsa uses the exact same tools like other images.
The main differences are:

 * It builds two root file systems, one for the high and one for the low integrity virtual machine
 * It configures the hypervisor to start the two virtual machines


The whole process is depicted in the image below
![EBCLFSA](../assets/ebclfsa.png)

This documentation will only describe the configuration of the hypervisor.

### Hypervisor configuration

### Step 1: Extract the hypervisor specialization

As described in the hypervisor config tool description, the tool allows specialization of the configuration model.
In the first step a tools root filesystem is generated.
The unconfigured hypervisor and the config specialization are installed in this filesystem.
At the end of this step the configuration specialization and the u-boot used to boot the image are extracted.

### Step 2: Generate the hypervisor configuration

In this step the extracted specialization is used together with the configuration yaml file (_hv/hv-qemu.yaml_) to generate all configuration files.

Parallel to this generation, the linux kernels for the high and low integrity VM are extracted and the initrd for the low integrity VM is generated.

### Step 3: Build the final hypervisor

For this step several files are copied into the generated tools filesystem in order to generate the final hypervisor binary.
These files are:

 * The generated configuration
 * The extracted kernels
 * The initrd for the low integrity VM
 * The device tree sources for the high and low integrity VM

These files are then processed by _config_hypervisor.sh_ inside of the tools root filesystem.
First the two device trees are compiled using linux's device tree compiler, then the configured hypervisor is generated.

At the end of this step the configured hypervisor is extracted from the tools filesystem, so it can be installed onto the boot partition by embdgen.
