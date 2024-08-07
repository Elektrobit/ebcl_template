*** Settings ***
Library  lib/CommManager.py  mode=Serial

Documentation  common keywords

*** Keywords ***
Run Qemu Image Raw
    [Arguments]    ${img}    ${arch}
    Test Setup  ${img}  raw  ${arch}

Run Qemu Image Qcow2
    [Arguments]    ${img}    ${arch}
    Test Setup  ${img}  qcow2  ${arch}

Setup
    Log  started
    Create Session  console
    Run Qemu Image Qcow2  images/reference_image_standard.aarch64-1.1.0-0.qcow2  aarch64
    Sleep    1s
