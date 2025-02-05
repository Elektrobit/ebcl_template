*** Settings ***
Resource    resources/image.resource
Test Timeout    15m

*** Test Cases ***

#==================================
# Tests for QEMU ARM64 Jammy images
#==================================
Build Image arm64/qemu/jammy
    [Tags]    arm64    qemu    debootstrap    jammy    systemd
    Test Systemd Image    arm64/qemu/jammy

#==================================
# Tests for QEMU ARM64 EBcL images
#==================================
Build Image arm64/qemu/ebcl/crinit
    [Tags]    arm64    qemu    crinit    ebcl    crinit
    Test Crinit Image    arm64/qemu/ebcl/crinit

#======================
# Tests for RDB2 images
#======================
# Build Image arm64/nxp/rdb2/network
#     [Tags]    arm64    rdb2    hardware    debootstrap    ebcl    crinit    network
#     [Timeout]    1h
#     Test Hardware Image    arm64/nxp/rdb2/network    build_timeout=1h

#================================
# Tests for Raspberry Pi 4 images
#================================
Build Image arm64/raspberry/pi4/crinit
    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    crinit    network
    [Timeout]    1h
    Test Hardware Image    arm64/raspberry/pi4/crinit    build_timeout=1h

Build Image arm64/raspberry/pi4/systemd
    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    systemd
    [Timeout]    1h
    Test Hardware Image    arm64/raspberry/pi4/systemd    build_timeout=1h

#========================
# Tests for appdev images
#========================
Build Image amd64/appdev/qemu/crinit
    [Tags]    amd64    qemu    debootstrap    crinit    ebcl    appdev
    Test Crinit Image    amd64/appdev/qemu/crinit

Build Image amd64/appdev/qemu/systemd
    [Tags]    amd64    qemu    debootstrap    systemd    ebcl    appdev
    Test Systemd Image    amd64/appdev/qemu/systemd

Build Image arm64/appdev/qemu/crinit
    [Tags]    arm64    qemu    debootstrap    crinit    ebcl    appdev
    Test Crinit Image    arm64/appdev/qemu/crinit

Build Image arm64/appdev/pi4
    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    crinit    appdev
    [Timeout]    1h
    Test Hardware Image    arm64/appdev/pi4    build_timeout=1h
