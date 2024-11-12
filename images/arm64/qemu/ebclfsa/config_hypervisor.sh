#!/bin/sh

# Compile the two device trees
dtc -I dts -O dtb -o config/hv_config/virt-li.dtb config/virt-li.dts
dtc -I dts -O dtb -o config/hv_config/virt-hi.dtb config/virt-hi.dts

mkdir -p /workdir
/usr/share/fiasco/tools/bin/l4image -i /usr/share/fiasco/qemu/images/bootstrap_noml.uimage --outputdir /workdir extract
/usr/share/fiasco/tools/bin/l4image \
    -i /usr/share/fiasco/qemu/images/bootstrap_noml.uimage \
    -o /bootstrap.uimage \
    create \
        --modules-list-file /config/hv_config/modules.list \
        --search-path /config/hv_config:/workdir

