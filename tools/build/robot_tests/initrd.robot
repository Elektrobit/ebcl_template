*** Settings ***
Library  lib/Fakeroot.py
Library  lib/Initrd.py
Suite Setup  Setup
Suite Teardown  Teardown

*** Variables ***
${KVERSION}  5.15.0-1023-s32-eb
${CONFIG}    ../data/initrd.yaml

*** Test Cases ***
Root Device is Mounted
    Device should be mounted  /dev/mmcblk0p2    /sysroot

Devices are Created
    File Should Exist    /dev/console    character special file
    File Should Exist    /dev/mmcblk1    block special file

Modules should be loaded
    File Should Exist    /lib/modules/${KVERSION}/kernel/pfeng/pfeng.ko
    Module Should Be Loaded    pfeng.ko

Rootfs should be set up
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

File dummy.txt should be OK
    Should Be Owned By   /root/dummy.txt    0    0
    Should Have Mode     /root/dummy.txt    666

File dummy should be OK
    Should Be Owned By   /root/other.txt    123    456
    Should Have Mode     /root/other.txt    777

*** Keywords ***
Setup
    Build Initrd    ${CONFIG}
    Load

Teardown
    Cleanup
