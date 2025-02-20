#!/bin/sh

# Link crinit as init
rm -f ./sbin/init
ln -s /usr/bin/crinit ./sbin/init
