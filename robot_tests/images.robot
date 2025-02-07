*** Settings ***
Resource    resources/image.resource
Test Timeout    30m

*** Test Cases ***

#==================================
# Tests for QEMU ARM64 images
#==================================
Build Image arm64/qemu/jammy
    [Tags]    arm64    qemu    debootstrap    jammy    systemd
    Test Systemd Image    arm64/qemu/jammy

Build Image arm64/qemu/noble
    [Tags]    arm64    qemu    debootstrap    noble    systemd
    Test Systemd Image    arm64/qemu/noble

Build Image arm64/qemu/ebcl
    [Tags]    arm64    qemu    crinit    ebcl    crinit
    Test Crinit Image    arm64/qemu/ebcl

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

Build Image arm64/appdev/qemu/systemd
    [Tags]    arm64    qemu    debootstrap    systemd    ebcl    appdev
    Test Crinit Image    arm64/appdev/qemu/systemd

Build Image arm64/appdev/raspberry/pi4
    [Tags]    arm64    pi4    hardware    debootstrap    ebcl    crinit    appdev
    [Timeout]    1h
    Test Hardware Image    arm64/appdev/raspberry/pi4    build_timeout=45m

#======================
# Tests for RDB2 images
#======================
Build Image arm64/nxp/rdb2
    [Tags]    arm64    rdb2    hardware    debootstrap    ebcl    crinit    network
    [Timeout]    1h
    Test Hardware Image    arm64/nxp/rdb2    build_timeout=1h

#================================
# Tests for Raspberry Pi 4 images
#================================
Build Image arm64/raspberry/pi4/ebcl
   [Tags]    arm64    pi4    hardware    debootstrap    ebcl    crinit    network
   [Timeout]    1h
   Test Hardware Image    arm64/raspberry/pi4/ebcl    build_timeout=50m

Build Image arm64/raspberry/pi4/jammy
   [Tags]    arm64    pi4    hardware    debootstrap    ebcl    systemd    jammy
   [Timeout]    1h
   Test Hardware Image    arm64/raspberry/pi4/jammy    build_timeout=50m

Build Image arm64/raspberry/pi4/noble
   [Tags]    arm64    pi4    hardware    debootstrap    ebcl    systemd    noble
   [Timeout]    1h
   Test Hardware Image    arm64/raspberry/pi4/noble    build_timeout=50m

#=================================
# Tests for BeagelBone AI64 images
#=================================

