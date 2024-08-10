# Configruation parameters

The following list gives an overview about the supported configuration parameters for the EB corbos Linux build helper tools. Embdgen is developed separately, and the details and options for the storage specification is documented in the [embdgen documentation](https://elektrobit.github.io/embdgen/index.html).

## Parameters supported by all build helpers

- **base** _(boot/initrd/root)_: Parent yaml file. All parameters specified in the base yaml file will be taken over as defaults when this yaml is parsed.
- **arch** _(boot/initrd/root)_:
- **apt_repos** _(boot/initrd/root)_:
- **ebcl_version** _(boot/initrd/root)_:
- **use_ebcl_apt** _(boot/initrd/root)_:

## Additional parameters for the boot and root generators

- **host_files** _(boot/root/config)_:
- **scripts** _(boot/root)_:

## Additional parameters for the boot and initrd generators

- **files** _(boot/initrd)_:

## Additional parameters for the initrd and root generators

- **template** _(initrd/root)_:
- **name** _(initrd/root)_:

## Additional parameters for the boot generator only

- **archive_name** _(boot)_ \[default: boot.tar\]:
- **download_deps** _(boot)_:
- **boot_tarball** _(boot)_:
- **boot_packages** _(boot)_:
- **use_packages** _(boot)_:
- **packages** _(boot)_:
- **kernel** _(boot)_:
- **tar** _(boot)_:

## Additional parameters for the initrd generator only

- **modules** _(initrd)_:
- **root_device** _(initrd)_:
- **devices** _(initrd)_:
- **files** _(initrd)_:
- **kversion** _(initrd)_:
- **modules_folder** _(initrd)_:
- **initrd_name** _(initrd)_:
- **fakeroot** _(initrd)_:
- **modules_packages** _(initrd)_:
- **busybox** _(initrd)_:
- **kernel** _(initrd)_:

## Additional parameters for the root generator and configrator only

- **result** _(root)_:
- **image** _(root)_:
- **berrymill_conf** _(root)_:
- **use_berrymill** _(root)_:
- **use_bootstrap_package** _(root)_:
- **bootstrap_package** _(root)_:
- **kiwi_root_overlays** _(root)_:
- **use_kiwi_defaults** _(root)_:
- **kvm** _(root)_:
- **image_version** _(root)_:
- **type** _(root)_:
- **primary_repo** _(root)_:
- **root_password** _(root)_:
- **hostname** _(root)_:
- **domain** _(root)_:
- **console** _(root)_:
- **packer** _(root)_:
- **packages** _(root)_:
- **bootstrap** _(root)_:
- **sysroot_packages** _(root)_:
- **sysroot_defaults** _(root)_:

saf

- **kiwi_scripts** _(root/config)_:
- **pack_in_chroot** _(root/config)_:

