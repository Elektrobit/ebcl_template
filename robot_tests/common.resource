*** Settings ***
Library  lib/CommManager.py  mode=Serial

Documentation  common keywords

*** Keywords ***
Run Qemu Image Raw
    [Arguments]    ${img}    ${arch}
    Test Setup    ${img}  raw  ${arch}

Run Qemu Image Qcow2
    [Arguments]    ${img}    ${arch}
    Test Setup    ${img}  qcow2  ${arch}
