#!/bin/sh

# Link crinit as init
rm -f ./sbin/init
ln -s /usr/bin/crinit ./sbin/init

apt update
cd /amd
chmod +x install_debs.sh
export DEBIAN_FRONTEND="noninteractive"
export TZ="Etc/UTC"
yes | ./install_debs.sh
