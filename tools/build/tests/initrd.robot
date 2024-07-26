*** Settings ***
Library  lib/Initrd.py
Suite Setup  Setup
Suite Teardown  Teardown

*** Variables ***
${KVERSION}  5.15.0-1023-s32-eb

*** Test Cases ***
Root Device is Mounted
    Device should be mounted  /dev/mmcblk0p2    /sysroot

Devices are Created
    File Should Exist    /dev/console    character special file
    File Should Exist    /dev/mmcblk1    block special file

Modules should be loaded
    File Should Exist    /lib/modules/${KVERSION}/kernel/pfeng/pfeng.ko
    Module Should Be Loaded    pfeng.ko

rootfs should be set up
    Directory Should Exist  /proc
    Directory Should Exist  /sys
    Directory Should Exist  /dev
    Directory Should Exist  /sysroot
    Directory Should Exist  /var
    Directory Should Exist  /tmp
    Directory Should Exist  /run
    Directory Should Exist  /root
    Directory Should Exist  /usr
    Directory Should Exist  /sbin
    Directory Should Exist  /lib
    Directory Should Exist  /etc

*** Keywords ***
Setup
    Build Initrd
    Load

Teardown
    Cleanup
