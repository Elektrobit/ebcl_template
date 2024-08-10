*** Settings ***
Library    lib/Fakeroot.py
Library    lib/CommManager.py    mode=Process
Test Timeout    1h

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
    [Timeout]    2h
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
    [Timeout]    1h
    Test Systemd Image    example-old-images/qemu/berrymill    root.qcow2

Build Image example-old-images/qemu/elbe/amd64
    [Tags]    amd64    qemu    elbe    jammy    old
    [Timeout]    1h
    Test Systemd Image    example-old-images/qemu/elbe/amd64    root.img

Build Image example-old-images/qemu/elbe/arm64
    [Tags]    arm64    qemu    elbe    jammy    old
    [Timeout]    1h
    Test Systemd Image    example-old-images/qemu/elbe/arm64    root.img

#======================
# Tests for RDB2 images
#======================
Build Image arm64/nxp/rdb2/systemd
    [Tags]    arm64    rdb2    hardware    elbe    ebcl
    Test Hardware Image    arm64/nxp/rdb2/systemd

Build Image arm64/nxp/rdb2/kernel_src
    [Tags]    arm64    rdb2    hardware    elbe    ebcl
    [Timeout]    2h
    Test Hardware Image    arm64/nxp/rdb2/kernel_src



*** Keywords ***
Run Make
    [Arguments]    ${path}    ${target}    ${max_time}=
    [Timeout]    ${max_time}
    ${result}=    Execute    source /build/venv/bin/activate; cd ${path}; make ${target}
    RETURN    ${result}

Build Image
    [Arguments]    ${path}    ${image}=image.raw    ${max_time}=1h
    [Timeout]    ${max_time}
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${results_folder}=    Evaluate    $full_path + '/build'
    Run Make    ${full_path}    clean    2m
    Run Make    ${full_path}    image    ${max_time}
    Sleep    10s    # Give some processing time to other processes.
    Wait For Line Containing    Image was written to 
    ${file_info}=    Execute    cd ${results_folder}; file ${image}
    Should Not Contain    ${file_info}    No such file
    Clear Lines    # Clear the output queue
    Sleep    1s

Test That Make Does Not Rebuild
    [Arguments]    ${path}
    [Timeout]    1m
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${output}=    Run Make    ${full_path}    image
    Should Contain    ${output}    Nothing to be done for 'image'

Run Image
    [Arguments]    ${path}    ${image}=image.raw
    [Timeout]    2m
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    Send Message    source /build/venv/bin/activate; cd ${full_path}; make qemu
    ${success}=    Login To Vm
    Should Be True    ${success}

Shutdown Systemd Image
    [Timeout]    1m
    Send Message    \nsystemctl poweroff
    Wait For Line Containing    System Power Off
    Sleep    1s

Test Systemd Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}    ${image}
    Shutdown Systemd Image
    Disconnect

Test Hardware Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
