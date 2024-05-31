# Overview

EB corbos Linux built on Ubuntu is a long-term maintained embedded Linux distribution focused on automotive ECUs. It provides security patches for a frozen package set for up to 15 years for a quite low pricing. To realize this, Elektrobit partners with Canonical. EB corbos Linux makes use of many Ubuntu packages, qualifies these packages for automotive use-cases in reference images, and adds additional embedded optimized components.

In contrast to IT Linux distributions, EB corbos Linux allows a user to create a completely customer use-case specific image from scratch, in a reproducible way. This is realized using this SDK. A full EB corbos Linux release, also container pre-qualified reference images which already implement typical automotive use-cases, to kick-start the development of new ECUs.

To realize this flexible and configurable image build, this SDK makes use of different existing open-source tools. With the current version the image builder [elbe](https://elbe-rfs.org/) and [kiwi-ng](https://osinside.github.io/kiwi/) are supported for image building, and [pbuilder](https://wiki.ubuntu.com/PbuilderHowto) is used for package building.
