# 5.4. QEMU Xen image

The Xen Hypervisor EB corbos Linux image (located in *images/amd64/qemu/xen*) is an example utilizing Xen Hypervisor ([https://xenproject.org/](https://xenproject.org/)).
It generates a host image (Dom0, the initial priviledged domain) with the Xen Hypervisor that starts and runs one guest (DomU, unpriviledged domain) image.

## How to build and run

1. Navigate to *images/amd64/qemu/xen* in the explorer view, right click on xen and select "Open in Integrated Terminal"
2. In the new terminal run `make qemu`. This will build the image and run it in qemu.
3. The console of the guest (DomU) can be accessed from the terminal using command `xl console 1` (see Xen management tool documentation at https://xenbits.xen.org/docs/4.16-testing/man/xl.1.html for further details).

## Buildprocess

Building the Xen Hypervisor EB corbos Linux image uses the same tools as other images.
The main differences are:

 * It builds two images: the host image and the guest image.
 * The guest image is included in the host image (located in */opt/images/domu.img*)
 * GRUB is configured to the EFI partition after the image build.
