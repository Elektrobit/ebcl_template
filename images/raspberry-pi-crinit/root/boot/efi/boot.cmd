# Ubuntu Classic RPi U-Boot script (for armhf and arm64)

# Expects to be called with the following environment variables set:
#
#  devtype              e.g. mmc/scsi etc
#  devnum               The device number of the given type
#  distro_bootpart      The partition containing the boot files
#                       (introduced in u-boot mainline 2016.01)
#  prefix               Prefix within the boot partiion to the boot files
#  kernel_addr_r        Address to load the kernel to
#  fdt_addr_r           Address to load the FDT to
#  ramdisk_addr_r       Address to load the initrd to.

#Set device tree address
# Take fdt addr from the prior stage boot loader, if available
if test -n "$fdt_addr"; then
  fdt addr ${fdt_addr}
  fdt move ${fdt_addr} ${fdt_addr_r}  # implicitly sets fdt active
else
  fdt addr ${fdt_addr_r}
fi
fdt get value bootargs /chosen bootargs

setenv bootargs " ${bootargs} quiet splash"

if test -z "${fk_image_locations}"; then
  setenv fk_image_locations ${prefix}
fi

for pathprefix in ${fk_image_locations}; do
  # Store the gzip header (1f 8b) in the kernel area for comparison to the
  # header of the image we load. Load "vmlinuz" into the portion of memory for
  # the RAM disk (because we want to uncompress to the kernel area if it's
  # compressed) and compare the word at the start
  mw.w ${kernel_addr_r} 0x8b1f  # little endian

  #Loading kernel
  if load ${devtype} ${devnum}:${distro_bootpart} ${ramdisk_addr_r} ${pathprefix}vmlinuz; then
    kernel_size=${filesize}

    #Determine whether the kernel image is compressed
    if cmp.w ${kernel_addr_r} ${ramdisk_addr_r} 1; then
      # gzip compressed image (NOTE: *not* a self-extracting gzip compressed
      # kernel, just a kernel image that has been gzip'd)
      echo "Decompressing kernel..."
      unzip ${ramdisk_addr_r} ${kernel_addr_r}
      setenv kernel_size ${filesize}
      setenv try_boot "booti"
    else
      # Possibly self-extracting or uncompressed; copy data into the kernel area
      # and attempt launch with bootz then booti
      echo "Copying kernel..."
      cp.b ${ramdisk_addr_r} ${kernel_addr_r} ${kernel_size}
      setenv try_boot "bootz booti"
    fi

    #Loading the root file system
    if load ${devtype} ${devnum}:${distro_bootpart} ${ramdisk_addr_r} ${pathprefix}initrd.img; then
      setenv ramdisk_param "${ramdisk_addr_r}:${filesize}"
    else
      setenv ramdisk_param "-"
    fi

    #Boot kernel
    for cmd in ${try_boot}; do
        echo "Booting Ubuntu (with ${cmd}) from ${devtype} ${devnum}:${partition}..."
        ${cmd} ${kernel_addr_r} ${ramdisk_param} ${fdt_addr_r}
    done
  fi
done
