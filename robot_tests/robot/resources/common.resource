*** Settings ***
Library    Comm.py
Library    Power.py
Library    Image.py
Library    Util.py
Library    Overlay.py
Resource    ./image.resource

*** Variables ***
${IMAGE_TYPE}    crinit
${IMAGE_ARCH}    arm64
${TEST_OVERLAY_FOLDER}    /workspace/images/test_extensions


*** Keywords ***
File Should Exist
    [Arguments]    ${file}
    ${rc} =  Execute  ls -l ${file}
    Should Not Contain    ${rc}  No such file or directory  msg="File doesn't exist"

Build Test Overlay
    [Timeout]    5m
    [Arguments]    ${build_target}    ${overlay_file}
    ${overlay}=    Build Overlay    ${build_target}    ${overlay_file}
    Should Not Be Empty    ${overlay}
    Log    "Using test overlay ${overlay}."
    RETURN    ${overlay}

Setup Suite
    [Timeout]    45m
    ${image}=    Build Image
    Should Not Be Empty    ${image}
    ${process}=    Power On    ${image}
    Connect    ${process}
    Login To Vm
    Sleep    30s    # Give the system some time to bring up network.

Setup Suite Without Login
    [Timeout]    45m
    ${image}=    Build Image
    Should Not Be Empty    ${image}
    ${process}=    Power On    ${image}
    Connect    ${process}
    Sleep    30s    # Give the system some time to bring up network.

Teardown Suite
    [Timeout]    2m
    Shutdown Image
    Disconnect
    Power Off

Shutdown Image
    [Timeout]    2m
    Log    Image Type: ${IMAGE_TYPE}
    IF    "${IMAGE_TYPE}" == "crinit"
        ${command}    Set Variable    crinit-ctl poweroff
        ${target}    Set Variable    Power down
    ELSE IF    "${IMAGE_TYPE}" == "systemd"
        ${command}    Set Variable    systemctl poweroff
        ${target}    Set Variable    System Power Off
    ELSE
        Fail    "Invalid image type: ${IMAGE_TYPE}"
    END
    Log    Shutting down the image using ${command} and waiting for ${target}...
    Send Message    \n${command}
    Wait For Line    ${target}
    Sleep    1s

Set Env Qemu Amd64
    Set Env    variable=EBCL_TC_IMAGE_KERNEL_CMDLINE    value=console=ttyS0
    Set Env    variable=EBCL_TC_QEMU_BIN    value=qemu-system-x86_64
    Set Env    variable=EBCL_TC_QEMU_PARAMS    value=-nographic 

Set Env Qemu Arm64
    Set Env    variable=EBCL_TC_IMAGE_KERNEL_CMDLINE    value=console=ttyAMA0
    Set Env    variable=EBCL_TC_QEMU_BIN    value=qemu-system-aarch64
    Set Env    variable=EBCL_TC_QEMU_PARAMS    value=-machine virt -cpu cortex-a72 -machine type=virt -nographic

Set Env Qemu
    Log    Image Arch: ${IMAGE_ARCH}
    IF    "${IMAGE_ARCH}" == "arm64"
        Set Env Qemu Arm64
    ELSE IF    "${IMAGE_ARCH}" == "amd64"
        Set Env Qemu Amd64
    ELSE
        Fail    "Invalid image architecture: ${IMAGE_TYPE}"
    END    
