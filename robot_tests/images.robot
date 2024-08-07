*** Settings ***
Library  lib/Fakeroot.py
Resource    common.resource

*** Test Cases ***
Build Image amd64/qemu/jammy/berrymill
    Build Image    amd64/qemu/jammy/berrymill

Build Image amd64/qemu/jammy/debootstrap
    Build Image    amd64/qemu/jammy/debootstrap

Build Image amd64/qemu/jammy/elbe
    Build Image    amd64/qemu/jammy/elbe

Build Image amd64/qemu/jammy/kernel_src
    Build Image    amd64/qemu/jammy/kernel_src

Build Image amd64/qemu/jammy/kiwi
    Build Image    amd64/qemu/jammy/kiwi



Build Image amd64/qemu/ebcl/systemd/berrymill
    Build Image    amd64/qemu/ebcl/systemd/berrymill

Build Image amd64/qemu/ebcl/systemd/elbe
    Build Image    amd64/qemu/ebcl/systemd/elbe



Build Image amd64/qemu/ebcl/crinit/elbe
    Build Image    amd64/qemu/ebcl/crinit/elbe



Build Image arm64/qemu/jammy/berrymill
    Build Image    arm64/qemu/jammy/berrymill

Build Image arm64/qemu/jammy/elbe
    Build Image    arm64/qemu/jammy/elbe



Build Image arm64/qemu/ebcl/systemd/berrymill
    Build Image    arm64/qemu/ebcl/systemd/berrymill

Build Image arm64/qemu/ebcl/systemd/elbe
    Build Image    arm64/qemu/ebcl/systemd/elbe



Build Image example-old-images/qemu/berrymill
    Build Image    example-old-images/qemu/berrymill

Build Image example-old-images/qemu/elbe/amd64
    Build Image    example-old-images/qemu/elbe/amd64

Build Image example-old-images/qemu/elbe/arm64
    Build Image    example-old-images/qemu/elbe/arm64



Run Image amd64/qemu/jammy/elbe
    Log    started
    Create Session    console
    
    Run Qemu Image Raw     /workspace/images/amd64/qemu/jammy/elbe/build/image.raw     x86_64
    
    Sleep    1s
    
    ${kernel_info}=    Execute    uname -a
    Should contain    ${kernel_info}    x86_64


*** Keywords ***
Build Image
    [Arguments]    ${path}
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${results_folder}=    Evaluate    $full_path + '/build'
    Run No Fake    rm -rf ${results_folder}
    Run No Fake    bash -c "source /build/venv/bin/activate; cd ${full_path}; make image"
    ${result}=    Run No Fake    file ${results_folder}/image.raw
    ${file_info}=    Evaluate    $result[0]
    Should Not Contain    ${file_info}    No such file
