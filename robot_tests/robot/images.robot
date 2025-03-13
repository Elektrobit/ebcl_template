*** Settings ***
Resource    resources/image.resource
Resource    resources/common.resource

Test Timeout    30m

*** Test Cases ***

#========================
# Tests for appdev images
#========================
Build Image amd64/appdev/qemu/ebcl_1.x_crinit
    [Tags]    amd64    qemu    crinit    ebcl    appdev    image-build
    Set Env Qemu Amd64
    Test Crinit Image    amd64/appdev/qemu/ebcl_1.x_crinit

Build Image amd64/appdev/qemu/ebcl_1.x_systemd
    [Tags]    amd64    qemu    systemd    ebcl    appdev    image-build
    Set Env Qemu Amd64
    Test Systemd Image    amd64/appdev/qemu/ebcl_1.x_systemd

Build Image arm64/appdev/qemu/ebcl_1.x_crinit
    [Tags]    arm64    qemu    crinit    ebcl    appdev    image-build
    Set Env Qemu Arm64
    Test Crinit Image    arm64/appdev/qemu/ebcl_1.x_crinit

Build Image arm64/appdev/qemu/ebcl_1.x_systemd
    [Tags]    arm64    qemu    systemd    ebcl    appdev    CI    image-build
    Set Env Qemu Arm64
    Test Systemd Image    arm64/appdev/qemu/ebcl_1.x_systemd

Build Image arm64/appdev/raspberry/pi4
    [Tags]    arm64    pi4    hardware    ebcl    crinit    appdev    image-build
    [Timeout]    1h
    Test Hardware Image    arm64/appdev/raspberry/pi4    build_timeout=45m

#======================
# Tests for RDB2 images
#======================
Build Image arm64/nxp/rdb2/ebcl_1.x_crinit
    [Tags]    arm64    rdb2    hardware    ebcl    crinit    image-build
    [Timeout]    130m
    Test Hardware Image    arm64/nxp/rdb2/ebcl_1.x_crinit    build_timeout=2h

Build Image arm64/nxp/rdb2/ebcl_1.x_systemd
    [Tags]    arm64    rdb2    hardware    ebcl    crinit    image-build
    [Timeout]    130m
    Test Hardware Image    arm64/nxp/rdb2/ebcl_1.x_systemd    build_timeout=2h


#==================================
# Tests for QEMU ARM64 images
#==================================
Build Image arm64/qemu/ebcl_1.x
    [Tags]    arm64    qemu    crinit    ebcl    crinit    image-build
    Set Env Qemu Arm64
    Test Crinit Image    arm64/qemu/ebcl_1.x

Build Image arm64/qemu/jammy
    [Tags]    arm64    qemu    jammy    systemd    image-build
    Set Env Qemu Arm64
    Test Systemd Image    arm64/qemu/jammy

Build Image arm64/qemu/noble
    [Tags]    arm64    qemu    noble    systemd    image-build
    Set Env Qemu Arm64
    Test Systemd Image    arm64/qemu/noble


#================================
# Tests for Raspberry Pi 4 images
#================================
Build Image arm64/raspberry/pi4/ebcl_1.x
   [Tags]    arm64    pi4    hardware    ebcl    crinit    image-build
   [Timeout]    1h
   Test Hardware Image    arm64/raspberry/pi4/ebcl_1.x    build_timeout=50m

Build Image arm64/raspberry/pi4/jammy
   [Tags]    arm64    pi4    hardware    ebcl    systemd    jammy    image-build
   [Timeout]    1h
   Test Hardware Image    arm64/raspberry/pi4/jammy    build_timeout=50m

Build Image arm64/raspberry/pi4/noble
   [Tags]    arm64    pi4    hardware    ebcl    systemd    noble    image-build
   [Timeout]    1h
   Test Hardware Image    arm64/raspberry/pi4/noble    build_timeout=50m
