*** Settings ***
Library    lib/Setup.py
Library    lib/Kiwi.py
Suite Setup        Setup
Suite Teardown    Teardown
Keyword Tags    kiwi

*** Test Cases ***

SDK shall provide Kiwi-ng and Berrymill
    [Tags]    fast
    Kiwi Is Available
    Berrymill Is Available

SDK shall support a local apr repository
    [Tags]    fast
    Local Apt Repo

SDK shall support box builds of images
    [Tags]    slow    image
    Berrymill Box Build

SDK shall support cross builds of images
    [Tags]    slow    image
    Berrymill Cross Build

SDK shall support kvm builds of images
    [Tags]    slow    image
    Berrymill Kvm Build

SDK shall support cross builds of sysroots
    [Tags]    slow
    Berrymill Cross Sysroot

SDK shall support kvm builds of sysroots
    [Tags]    slow
    Berrymill Kvm Sysroot

SDK shall successfully build the QEMU systemd images
    [Tags]    slow    image
    Berrymill Cross Build Image    qemu-systemd-aarch64/appliance.kiwi    qemu_systemd_aarch64
    Berrymill Kvm Build Image    qemu-systemd-x86_64/appliance.kiwi    qemu_systemd_x86_64

SDK shall successfully build the Raspberry PI 4 images
    [Tags]    slow    image
    Berrymill Cross Build Image    raspberry-pi-crinit/appliance.kiwi    raspberry_pi_crinit
    Berrymill Cross Build Image    raspberry-pi-systemd/appliance.kiwi    raspberry_pi_systemd

SDK shall successfully build the NXP RDB2 images
    [Tags]    slow    image
    Berrymill Cross Build Image    rdb2-crinit/appliance.kiwi    rdb2_crinit
    Berrymill Cross Build Image    rdb2-systemd/appliance.kiwi    rdb2_systemd

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
