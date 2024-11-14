# Building old Berrymill images

The previous versions of the EBcL SDK used _kiwi-ng_ for building images.
Using _kiwi-ng_ was a quite pragmatic choice, since it’s an established tool to build images from binary IT distribution packages. Nevertheless, it turned out that _kiwi-ng_ is not flexible enough to build typical embedded images.
Starting from EBcL SDK 1.3 the new _make_ and _generator_ based builds are used.
This approach has the advantage that it’s flexible enough for any imaginable build flow, and that the builds are much more efficient.
Nevertheless, at least for EBcL 1.x, _kiwi-ng_ is still provided and supported.
If you are at the very beginning of your development, we recommend switching to the new build flow, since it is more efficient, and _kiwi-ng_ support will be most likely dropped with the EBcL 2.x line.

For a stepwise transition, you can use the new build tools to build your existing _kiwi-ng_ images.
The folder _images/example-old-images/qemu/berrymill_ contains an example showing how to build an old _berrymill_ and _kiwi-ng_ image using the new tools.

```yaml
# Use Berrymill and Kiwi as image builder
type: kiwi
# Use KVM accelerated building - turn of if not supported on your host
kvm: true
# CPU architecture of the target
arch: 'amd64'
# Relative path to the kiwi appliance
image: appliance.kiwi
# Relative path to the berrymill.conf
berrymill_conf: berrymill.conf
# Result file name pattern
result_pattern: '*.qcow2'
```

The _root generator_ supports a parameter called “image”, with the path to the _appliance.kiwi_  as value.
An existing _berrymill.conf_ can be provided using the parameter “berrymill_conf”. The old images typically used _qcow2_ results, and the parameter “result_pattern” can be used to tell the _root generator_ to search for such files.
 Using this his _root.yaml_, the _root generator_ will run a _berrymill_ build for the given _appliance.kiwi_, and the results will be placed in the given output folder.
This call of the _root generator_, and the instructions to run the resulting image with QEMU, are contained in the example _Makefile_. The “ --no-config” is needed to tell the _root generator_ to not extract the result and apply the configuration, since this will be already done as part of the _kiwi-ng_ build.
 
