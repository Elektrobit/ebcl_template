#!/bin/dash

set -ex

#=======================================
# Set zstd as compression for dracut
#---------------------------------------
mkdir -p /etc/dracut.conf.d/
cat > /etc/dracut.conf.d/50-enable-zstd-compression.conf << EOF
compress="zstd"
EOF
