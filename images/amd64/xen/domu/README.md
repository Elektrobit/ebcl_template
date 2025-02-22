# DomU image

The domu image supports a local QEMU variant and a XEN VM variant.

## QEMU

- Edit _root.yaml_:
    - un-comment `# - source: grub_qemu/*`
    - comment `- source: grub_xen/*`
- Build the image: `task build`
- Run image in QEMU:
    - `task qemu`
    - Select "Advance options..."
    - Select the Canonical kernel, not the amd+ kernel. Login in the amd+ kernel doesn't work.

## XEM

- Edit _root.yaml_:
    - comment `- source: grub_qemu/*`
    - un-comment `# - source: grub_xen/*`
- Build the image: `task build`
- Build and run the Dom0 image.

