*** Settings ***
Library    lib/Fakeroot.py
Library    lib/CommManager.py    mode=Process
Test Timeout    45m

*** Test Cases ***

#==================================
# Tests for QEMU AMD64 Jammy images
#==================================
Build Image amd64/qemu/jammy/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    jammy    systemd
    Test Systemd Image    amd64/qemu/jammy/berrymill

Build Image amd64/qemu/jammy/debootstrap
    [Tags]    amd64    qemu    berrymill    kiwi    jammy    systemd
    Test Systemd Image    amd64/qemu/jammy/debootstrap

Build Image amd64/qemu/jammy/elbe
    [Tags]    amd64    qemu    elbe    jammy
    Test Systemd Image    amd64/qemu/jammy/elbe

Build Image amd64/qemu/jammy/kiwi
    [Tags]    amd64    qemu    kiwi    jammy    systemd
    Test Systemd Image    amd64/qemu/jammy/kiwi

#==================================
# Tests for QEMU AMD64 EBcL images
#==================================
Build Image amd64/qemu/ebcl/systemd/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl    systemd
    Test Systemd Image    amd64/qemu/ebcl/systemd/berrymill

Build Image amd64/qemu/ebcl/systemd/elbe
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl    systemd
    Test Systemd Image    amd64/qemu/ebcl/systemd/elbe

Build Image amd64/qemu/ebcl/crinit/berrymill
    [Tags]    amd64    qemu    crinit    ebcl    crinit
    Test Crinit Image    amd64/qemu/ebcl/crinit/berrymill

Build Image amd64/qemu/ebcl/crinit/elbe
    [Tags]    amd64    qemu    elbe    ebcl    crinit
    Test Crinit Image    amd64/qemu/ebcl/crinit/elbe

Build Image amd64/qemu/ebcl/server
    [Tags]    amd64    qemu    elbe    ebcl    crinit    server
    Test Crinit Image    amd64/qemu/ebcl/server

Build Image amd64/qemu/ebcl/server/systemd
    [Tags]    amd64    qemu    elbe    ebcl    systemd    server
    Test Systemd Image    amd64/qemu/ebcl/server/systemd

#==================================
# Tests for QEMU ARM64 Jammy images
#==================================
Build Image arm64/qemu/jammy/berrymill
    [Tags]    arm64    qemu    berrymill    kiwi    jammy    systemd
    Test Systemd Image    arm64/qemu/jammy/berrymill

Build Image arm64/qemu/jammy/elbe
    [Tags]    arm64    qemu    elbe    jammy    systemd
    Test Systemd Image    arm64/qemu/jammy/elbe

#==================================
# Tests for QEMU ARM64 EBcL images
#==================================
Build Image arm64/qemu/ebcl/systemd/berrymill
    [Tags]    arm64    qemu    berrymill    kiwi    ebcl    systemd
    Test Systemd Image    arm64/qemu/ebcl/systemd/berrymill

Build Image arm64/qemu/ebcl/systemd/elbe
    [Tags]    arm64    qemu    elbe    ebcl    systemd
    Test Systemd Image    arm64/qemu/ebcl/systemd/elbe

Build Image arm64/qemu/ebcl/crinit/berrymill
    [Tags]    arm64    qemu    crinit    ebcl    crinit
    Test Crinit Image    arm64/qemu/ebcl/crinit/berrymill

Build Image arm64/qemu/ebcl/crinit/elbe
    [Tags]    arm64    qemu    crinit    ebcl    crinit
    Test Crinit Image    arm64/qemu/ebcl/crinit/elbe

#==================================
# Tests for old format images
#==================================
Build Image example-old-images/qemu/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl    old
    [Timeout]    60m
    ${path}=    Set Variable    example-old-images/qemu/berrymill
    # ---------------
    # Build the image
    # ---------------
    ${full_path}=    Set Variable    /workspace/images/example-old-images/qemu/berrymill
    ${results_folder}=    Evaluate    $full_path + '/build'
    Connect
    # Remove old build artefacts - build from scratch
    Run Make    ${full_path}    clean    2m 
    # Build the image
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make image
    # Check for Embdgen log
    Should Contain    ${result}    Image was written to
    Sleep    1s
    # Check that image file exists
    ${file_info}=    Execute    cd ${results_folder}; file root.qcow2
    Should Not Contain    ${file_info}    No such file
    # Clear the output queue
    Clear Lines    
    Sleep    1s
    # -------------
    # Run the image
    # -------------
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}
    Send Message    \ncrinit-ctl poweroff
    Sleep    20s
    Disconnect

#======================
# Tests for RDB2 images
#======================
Build Image arm64/nxp/rdb2/systemd
    [Tags]    arm64    rdb2    hardware    elbe    ebcl    systemd
    Test Hardware Image    arm64/nxp/rdb2/systemd

Build Image arm64/nxp/rdb2/crinit
    [Tags]    arm64    rdb2    hardware    elbe    ebcl    crinit
    Test Hardware Image    arm64/nxp/rdb2/crinit

Build Image arm64/nxp/rdb2/network
    [Tags]    arm64    rdb2    hardware    elbe    ebcl    crinit    network
    Test Hardware Image    arm64/nxp/rdb2/network

#================================
# Tests for Raspberry Pi 4 images
#================================
Build Image arm64/raspberry/pi4/crinit
    [Tags]    arm64    pi4    hardware    elbe    ebcl    crinit    network
    Test Hardware Image    arm64/raspberry/pi4/crinit

Build Image arm64/raspberry/pi4/systemd
    [Tags]    arm64    pi4    hardware    elbe    ebcl    systemd
    Test Hardware Image    arm64/raspberry/pi4/systemd

#==========================================
# Tests for images using local built kernel
#==========================================
Build Image amd64/qemu/jammy/kernel_src
    [Tags]    amd64    qemu   elbe    jammy    systemd    kernel_src
    [Timeout]    2h
    Connect
    ${path}=    Set Variable    amd64/qemu/jammy/kernel_src
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${results_folder}=    Evaluate    $full_path + '/build'
    # Remove old build artefacts - build from scratch
    Run Make    ${full_path}    clean    2m 
    # Build the initrd
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make initrd
    # Check for boot generator log
    Should Contain    ${result}    Image was written to
    Sleep    1s
    # Build the kernel
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make boot
    Sleep    1s
    # Build the image
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make image
    # Check for Embdgen log
    Should Contain    ${result}    Writing image to
    Sleep    1s
    # Check that image file exists
    ${file_info}=    Execute    cd ${results_folder}; file image.raw
    Should Not Contain    ${file_info}    No such file
    # Clear the output queue
    Clear Lines    
    Sleep    1s
    Test That Make Does Not Rebuild    amd64/qemu/jammy/kernel_src
    Run Image    amd64/qemu/jammy/kernel_src
    Shutdown Systemd Image
    Disconnect

Build Image arm64/nxp/rdb2/kernel_src
    [Tags]    arm64    rdb2    hardware    elbe    ebcl    systemd    kernel_src
    [Timeout]    90m
    Test Hardware Image    arm64/nxp/rdb2/kernel_src



*** Keywords ***
Run Make
    [Arguments]    ${path}    ${target}    ${max_time}=2h
    [Timeout]    ${max_time}
    ${result}=    Execute    source /build/venv/bin/activate; cd ${path}; make ${target}
    RETURN    ${result}

Build Image
    [Arguments]    ${path}    ${image}=image.raw    ${max_time}=1h
    [Timeout]    ${max_time}
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${results_folder}=    Evaluate    $full_path + '/build'
    
    # Remove old build artefacts - build from scratch
    Run Make    ${full_path}    clean    2m 

    # Build the initrd
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make initrd
    # Check for boot generator log
    Should Contain    ${result}    Image was written to

    Sleep    1s

    # Build the kernel
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make boot
    # Check for boot generator log
    Should Contain    ${result}    Results were written to

    Sleep    1s

    # Build the image
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make image
    # Check for Embdgen log
    Should Contain    ${result}    Writing image to

    Sleep    1s
    
    # Check that image file exists
    ${file_info}=    Execute    cd ${results_folder}; file ${image}
    Should Not Contain    ${file_info}    No such file
    
    # Clear the output queue
    Clear Lines    
    Sleep    1s

Test That Make Does Not Rebuild
    [Arguments]    ${path}
    [Timeout]    1m
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${output}=    Run Make    ${full_path}    image
    Should Contain    ${output}    Nothing to be done for 'image'

Run Image
    [Arguments]    ${path}
    [Timeout]    5m
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    Send Message    source /build/venv/bin/activate; cd ${full_path}; make qemu
    ${success}=    Login To Vm
    Should Be True    ${success}

Shutdown Systemd Image
    [Timeout]    2m
    Send Message    \nsystemctl poweroff
    Wait For Line Containing    System Power Off
    Sleep    1s

Test Systemd Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}
    Shutdown Systemd Image
    Disconnect

Shutdown Crinit Image
    [Timeout]    2m
    Send Message    \ncrinit-ctl poweroff
    Wait For Line Containing    Power down
    Sleep    1s

Test Crinit Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}
    Shutdown Crinit Image
    Disconnect

Test Hardware Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
