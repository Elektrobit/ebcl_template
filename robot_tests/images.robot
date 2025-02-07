*** Settings ***
Resource    resources/image.resource
Test Timeout    30m

*** Test Cases ***

#========================
# Tests for appdev images
#========================
Build Image amd64/appdev/qemu/ebcl_1.x_crinit
    [Tags]    amd64    qemu    debootstrap    crinit    ebcl    appdev
    Test Crinit Image    amd64/appdev/qemu/ebcl_1.x_crinit

Build Image amd64/appdev/qemu/ebcl_1.x_systemd
    [Tags]    amd64    qemu    debootstrap    systemd    ebcl    appdev
    Test Systemd Image    amd64/appdev/qemu/ebcl_1.x_systemd

Build Image arm64/appdev/qemu/ebcl_1.x_crinit
    [Tags]    arm64    qemu    debootstrap    crinit    ebcl    appdev
    Test Crinit Image    arm64/appdev/qemu/ebcl_1.x_crinit

Build Image arm64/appdev/qemu/ebcl_1.x_systemd
    [Tags]    arm64    qemu    debootstrap    systemd    ebcl    appdev
    Test Systemd Image    arm64/appdev/qemu/ebcl_1.x_systemd

Build Image arm64/appdev/raspberry/pi4
    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    crinit    appdev
    [Timeout]    1h
    Test Hardware Image    arm64/appdev/raspberry/pi4    build_timeout=45m

#=================================
# Tests for BeagleBone AI64 images
#=================================
# Build Image arm64/beaglebone/ai64/packages_ebcl_1.x_crinit
#     [Tags]    arm64    bbai64    hardware    debootstrap    ebcl    crinit
#     Test Hardware Image    arm64/beaglebone/ai64/packages_ebcl_1.x_crinit    build_timeout=45m

# Build Image arm64/beaglebone/ai64/yocto_ebcl_1.x_crinit
#     [Tags]    arm64    bbai64    hardware    debootstrap    ebcl    crinit
#     Test Hardware Image    arm64/beaglebone/ai64/yocto_ebcl_1.x_crinit    build_timeout=45m


#======================
# Tests for RDB2 images
#======================
Build Image arm64/nxp/rdb2/ebcl_1.x_crinit
    [Tags]    arm64    rdb2    hardware    debootstrap    ebcl    crinit    network
    [Timeout]    1h
    Test Hardware Image    arm64/nxp/rdb2/ebcl_1.x_crinit    build_timeout=1h

Build Image arm64/nxp/rdb2/ebcl_1.x_systemd
    [Tags]    arm64    rdb2    hardware    debootstrap    ebcl    crinit    network
    [Timeout]    1h
    Test Hardware Image    arm64/nxp/rdb2/ebcl_1.x_systemd    build_timeout=1h


#==================================
# Tests for QEMU ARM64 images
#==================================
Build Image arm64/qemu/ebcl_1.x
    [Tags]    arm64    qemu    crinit    ebcl    crinit
    Test Crinit Image    arm64/qemu/ebcl_1.x

Build Image arm64/qemu/jammy
    [Tags]    arm64    qemu    debootstrap    jammy    systemd
    Test Systemd Image    arm64/qemu/jammy

Build Image arm64/qemu/noble
    [Tags]    arm64    qemu    debootstrap    noble    systemd
    Test Systemd Image    arm64/qemu/noble


#================================
# Tests for Raspberry Pi 4 images
#================================
# Build Image arm64/raspberry/pi4/ebcl_1.x
#    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    crinit    network
#    [Timeout]    1h
#    Test Hardware Image    arm64/raspberry/pi4/ebcl_1.x    build_timeout=50m

# Build Image arm64/raspberry/pi4/jammy
#    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    systemd    jammy
#    [Timeout]    1h
#    Test Hardware Image    arm64/raspberry/pi4/jammy    build_timeout=50m

# Build Image arm64/raspberry/pi4/noble
#    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    systemd    noble
#    [Timeout]    1h
#    Test Hardware Image    arm64/raspberry/pi4/noble    build_timeout=50m

#================================
# Tests for Raspberry Pi 5 images
#================================
# Build Image arm64/raspberry/pi5/ebcl_1.x
#    [Tags]    arm64    pi5    hardware    debootstrap    ebcl    crinit    network
#    [Timeout]    1h
#    Test Hardware Image    arm64/raspberry/pi5/ebcl_1.x    build_timeout=50m

# Build Image arm64/raspberry/pi5/jammy
#    [Tags]    arm64    pi5    hardware    debootstrap    ebcl    systemd    jammy
#    [Timeout]    1h
#    Test Hardware Image    arm64/raspberry/pi5/jammy    build_timeout=50m

# Build Image arm64/raspberry/pi5/noble
#    [Tags]    arm64    pi5    hardware    debootstrap    ebcl    systemd    noble
#    [Timeout]    1h
#    Test Hardware Image    arm64/raspberry/pi5/noble    build_timeout=50m
