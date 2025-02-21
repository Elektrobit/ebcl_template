*** Settings ***
Resource    resources/image-build.robot
Test Timeout    45m
*** Test Cases ***

#====================================
# Test for QEMU ARM64 EBcLfSA image
#====================================
Build Image arm64/qemu/ebclfsa x10 times
    
    [Tags]    arm64    qemu    debootstrap    ebclfsa
    FOR     ${index}    IN RANGE    10
    Build Image    arm64/qemu/ebclfsa
    END
