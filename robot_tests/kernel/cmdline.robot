*** Settings ***
Suite Setup  Setup
Library  ../lib/CommManager.py  mode=Serial

*** Variables ***
${cmdline}  /proc/cmdline
${rootdev}  /dev/vda1
*** Test Cases ***
Linux kernel cmdline exists
    File Should Exist      ${cmdline}

Root device is created
    File Should Exist      ${rootdev}

Print cmdline
     ${cl} =  Execute   cat ${cmdline}
     Should Contain    ${cl}  root=



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



File Should Exist
    [Arguments]    ${arg1}
    ${rc} =  Execute  ls -l ${arg1}
    Should Not Contain    ${rc}  No such file or directory  msg="File doesn't exist"