# Overview

EB corbos Linux built on Ubuntu is a long-term maintained embedded Linux distribution focused on automotive ECUs. It provides security patches for a frozen package set for up to 15 years for a quite low pricing. To realize this, Elektrobit partners with Canonical. EB corbos Linux makes use of many Ubuntu packages, qualifies these packages for automotive use-cases in reference images, and adds additional embedded optimized components.

In contrast to IT Linux distributions, EB corbos Linux allows a user to create a completely customer use-case specific image from scratch, in a reproducible way. This is realized using this SDK.

A free variant of EB corbos Linux is available at the [Elektrobit homepage](https://www.elektrobit.com/products/ecu/eb-corbos/linux-built-on-ubuntu/). The free variant doesn't contain proprietary hardware drivers or pre-qualified reference images.

To kick-start the development of new ECUs, a full EB corbos Linux release also contains pre-qualified reference images which already implement typical automotive use-cases. Please contact [Elektrobit sales](https://www.elektrobit.com/contact-us/) to get a full evaluation package for EB corbos Linux.

To realize a flexible and configurable image build, this SDK makes use of different existing open-source tools. With the current version the image builders [elbe](https://elbe-rfs.org/) and [kiwi-ng](https://osinside.github.io/kiwi/) are supported, and [pbuilder](https://wiki.ubuntu.com/PbuilderHowto) is used for packaging applications.
