# Developing images

EB corbos Linux is intended as _embedded Linux distribution build kit_, like _Yocto_ is.
Instead of starting form a pre-defined and pre-configured already integrated image, you describe
what you need, and build a embedded Linux distribution tailored to your needs.
In comparison to _Yocto_, where all packages are build form scratch, EB corbos Linux is using
the packages from the _Canonical Ubuntu_ distribution.

This has the advantage that you use the same binaries used by the millions of server in the cloud,
and the millions of single board computers around, and share the maintenance and qualificaition
effort with all these users.

To keep this advantage, you need to stay with the prebuild binaries, and accept the limiations caused
by this, but if necessary you can drop the advantage for a few packages, and adapt and rebuild
these packages to your needs. How to do this will be described in later chapters. This chapter assumes
that you use the available pre-build and pre-qualified packages.

This SDK version provides two tools for image building, [elbe](https://elbe-rfs.org/) and [kiwi-ng](https://osinside.github.io/kiwi/).

[kiwi-ng](https://osinside.github.io/kiwi/) is a tool form the Suse Linux world, but supports multiple package formats.
It was the exclusive image build tool in previous versions of this SDK, but it's focused on building images
for the server world and has poor performance when building images for non-native CPU architectures.
Some of the draw-backs of [kiwi-ng](https://osinside.github.io/kiwi/) were covered with [berrymill](https://github.com/isbm/berrymill),
but by far not all.

The draw-backs of [kiwi-ng](https://osinside.github.io/kiwi/) for embedded Linux images caused that we
introduce [elbe](https://elbe-rfs.org/) in this SDK version. [elbe](https://elbe-rfs.org/) is limited to
the Debian package format, but it's focused on building iamges for embedded Linux usage, and it
has a great performance for cross-building images.

## The old way: Developling images with [kiwi-ng](https://osinside.github.io/kiwi/)

You can find example EB corbos Linux images for [kiwi-ng](https://osinside.github.io/kiwi/) in the `images` folder
of the template.



## The new way: Developling images with [elbe](https://elbe-rfs.org/)

## Converting a image description from [kiwi-ng](https://osinside.github.io/kiwi/) to [elbe](https://elbe-rfs.org/)

The image descriptions of [kiwi-ng](https://osinside.github.io/kiwi/) and [elbe](https://elbe-rfs.org/) use different tags,
but are very similar form the basic ideas, and converting a [kiwi-ng](https://osinside.github.io/kiwi/) to [elbe](https://elbe-rfs.org/)
is straight forward.