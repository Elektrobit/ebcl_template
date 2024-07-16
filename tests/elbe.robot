*** Settings ***
Library    lib/Setup.py
Library    lib/Elbe.py
Suite Setup        Setup
Suite Teardown    Teardown
Keyword Tags    elbe

*** Test Cases ***

SDK shall provide elbe
    [Tags]    fast
    Elbe Is Available

SDK shall support cross building with binfmt
    [Tags]    fast
    Check Binfmt Works

SDK shall support amd64 image building
    [Tags]    slow    image
    Build Image Amd64

SDK shall support arm64 image building
    [Tags]    slow    image
    Build Image Arm64

SDK shall successfully build the Ubuntu Jammy image
    [Tags]    slow    image
    Elbe Build Image    /tmp/build/images/elbe/qemu/systemd/jammy-aarch64.xml    jammy-aarch64.xml

SDK shall successfully build the systemd images
    [Tags]    slow    image
    Elbe Build Image    /tmp/build/images/elbe/qemu/systemd/ebcl-systemd-aarch64.xml    ebcl-systemd-aarch64.xml
    Elbe Build Image    /tmp/build/images/elbe/qemu/systemd/ebcl-systemd-grub-aarch64.xml    ebcl-systemd-grub-aarch64.xml

SDK shall successfully build the crinit images
    [Tags]    slow    image
    Elbe Build Image    /tmp/build/images/elbe/qemu/crinit/ebcl-crinit-aarch64.xml    ebcl-crinit-aarch64.xml

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
