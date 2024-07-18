# Overview

EB corbos Linux built on Ubuntu is a long-term maintained embedded Linux distribution focused on automotive ECUs. It provides security patches for a frozen package set for up to 15 years on a quite low pricing. To realize this, Elektrobit partners with Canonical. EB corbos Linux makes use of many Ubuntu packages, qualifies these packages for automotive embedded use-cases in reference images, and adds additional embedded optimized components, to create an industry grade embedded Linux build toolkit.

In contrast to IT Linux distributions, EB corbos Linux allows a user to create a completely customer specific image from scratch in a reproducible way. This is realized using this SDK.

A free variant of EB corbos Linux is available at the [Elektrobit homepage](https://www.elektrobit.com/products/ecu/eb-corbos/linux-built-on-ubuntu/). The free variant doesn't contain proprietary hardware drivers or pre-qualified reference images.

To kick-start the development of new ECUs, a full EB corbos Linux release also contains pre-qualified reference images which already implement typical automotive use-cases. Please contact [Elektrobit sales](https://www.elektrobit.com/contact-us/) to get a full evaluation package of EB corbos Linux.

[This repository](https://github.com/Elektrobit/ebcl_template/) provides a template workspace to start developing your own Linux images and applications. It's based on a dev container to provide a consistent build environment. This dev container can also be used stand-alone with other IDEs or in CI environments. For more details about the container and stand-alone usage look at the dev container chapter.
