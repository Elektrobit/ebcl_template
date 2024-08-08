*** Settings ***
Library    lib/Fakeroot.py
Library    lib/CommManager.py    mode=Process

*** Test Cases ***

#==================================
# Tests for QEMU AMD64 Jammy images
#==================================
Build Image amd64/qemu/jammy/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    jammy
    Test Systemd Image    amd64/qemu/jammy/berrymill

Build Image amd64/qemu/jammy/debootstrap
    [Tags]    amd64    qemu    berrymill    kiwi    jammy
    Test Systemd Image    amd64/qemu/jammy/debootstrap

Build Image amd64/qemu/jammy/elbe
    [Tags]    amd64    qemu    elbe    jammy
    Test Systemd Image    amd64/qemu/jammy/elbe

Build Image amd64/qemu/jammy/kernel_src
    [Tags]    amd64    qemu   elbe    jammy
    Test Systemd Image    amd64/qemu/jammy/kernel_src

Build Image amd64/qemu/jammy/kiwi
    [Tags]    amd64    qemu    kiwi    jammy
    Test Systemd Image    amd64/qemu/jammy/kiwi

#==================================
# Tests for QEMU AMD64 EBcL images
#==================================
Build Image amd64/qemu/ebcl/systemd/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl
    Test Systemd Image    amd64/qemu/ebcl/systemd/berrymill

Build Image amd64/qemu/ebcl/systemd/elbe
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl
    Test Systemd Image    amd64/qemu/ebcl/systemd/elbe

#==================================
# Tests for QEMU ARM64 Jammy images
#==================================
Build Image arm64/qemu/jammy/berrymill
    [Tags]    arm64    qemu    berrymill    kiwi    jammy
    Test Systemd Image    arm64/qemu/jammy/berrymill

Build Image arm64/qemu/jammy/elbe
    [Tags]    arm64    qemu    elbe    jammy
    Test Systemd Image    arm64/qemu/jammy/elbe

#==================================
# Tests for QEMU ARM64 EBcL images
#==================================
Build Image arm64/qemu/ebcl/systemd/berrymill
    [Tags]    arm64    qemu    berrymill    kiwi    ebcl
    Test Systemd Image    arm64/qemu/ebcl/systemd/berrymill

Build Image arm64/qemu/ebcl/systemd/elbe
    [Tags]    arm64    qemu    elbe    ebcl
    Test Systemd Image    arm64/qemu/ebcl/systemd/elbe

#==================================
# Tests for old format images
#==================================
Build Image example-old-images/qemu/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl    old
    Test Systemd Image    example-old-images/qemu/berrymill    root.qcow2

Build Image example-old-images/qemu/elbe/amd64
    [Tags]    amd64    qemu    elbe    jammy    old
    Test Systemd Image    example-old-images/qemu/elbe/amd64    root.img

Build Image example-old-images/qemu/elbe/arm64
    [Tags]    arm64    qemu    elbe    jammy    old
    Test Systemd Image    example-old-images/qemu/elbe/arm64    root.img

*** Keywords ***
Build Image
    [Arguments]    ${path}    ${image}=image.raw
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${results_folder}=    Evaluate    $full_path + '/build'
    # TODO: enable clean to build everything from scratch
    # Run    bash -c "source /build/venv/bin/activate; cd ${full_path}; make clean"
    Run    bash -c "source /build/venv/bin/activate; cd ${full_path}; make image"
    ${result}=    Run    file ${results_folder}/image.raw
    ${file_info}=    Evaluate    $result[0]
    Should Not Contain    ${file_info}    No such file

Run Image
    [Arguments]    ${path}    ${image}=image.raw
    [Timeout]    120s
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    Send Message    cd ${full_path}
    Send Message    make qemu
    ${success}=    Login To Vm
    Should Be True    ${success}

Shutdown Systemd Image
    [Timeout]    30s
    Send Message    \nsystemctl poweroff
    Wait For Line Containing    System Power Off
    Sleep    1s

Test Systemd Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}
    Run Image    ${path}
    Shutdown Systemd Image
    Disconnect
