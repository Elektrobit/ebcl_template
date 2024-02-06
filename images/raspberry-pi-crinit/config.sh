#!/bin/bash
set -ex

echo "Configure image: [$kiwi_iname]..."

#======================================
# add missing fonts
#--------------------------------------
CONSOLE_FONT="eurlatgr.psfu"

#======================================
# Install firmware
#--------------------------------------
dpkg -i /var/tmp/firmware/linux-firmware-raspi_6-0ubuntu3_arm64.deb
dpkg -i /var/tmp/firmware/linux-firmware-raspi2_6-0ubuntu3_arm64.deb

# On Debian based distributions the kiwi built in way
# to setup locale, keyboard and timezone via systemd tools
# does not work because not(yet) provided by the distribution.
# Thus the following manual steps to make the values provided
# in the image description effective needs to be done.
#
#=======================================
# Setup system locale
#---------------------------------------
echo "LANG=${kiwi_language}" > /etc/locale.conf

#=======================================
# Setup system keymap
#---------------------------------------
echo "KEYMAP=${kiwi_keytable}" > /etc/vconsole.conf
echo "FONT=eurlatgr.psfu" >> /etc/vconsole.conf
echo "FONT_MAP=" >> /etc/vconsole.conf
echo "FONT_UNIMAP=" >> /etc/vconsole.conf

#=======================================
# Setup system timezone
#---------------------------------------
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/${kiwi_timezone} /etc/localtime

#=======================================
# Setup HW clock to UTC
#---------------------------------------
echo "0.0 0 0.0" > /etc/adjtime
echo "0" >> /etc/adjtime
echo "UTC" >> /etc/adjtime

#======================================
# Sysconfig Update
#--------------------------------------
# Systemd controls the console font now
echo FONT="$CONSOLE_FONT" >> /etc/vconsole.conf

# Work around HDMI connector bug and network issues
# No HDMI hotplug available
# Prevent too many page allocations (bsc#1012449)
cat > /etc/modprobe.d/50-rpi3.conf <<-EOF
    options drm_kms_helper poll=0
    options smsc95xx turbo_mode=N
EOF

# Avoid running out of DMA pages for smsc95xx (bsc#1012449)
cat > /usr/lib/sysctl.d/50-rpi3.conf <<-EOF
    vm.min_free_kbytes = 2048
EOF

#==================================
# Allow suid tools with busybox
#----------------------------------
chmod u+s /usr/bin/busybox
