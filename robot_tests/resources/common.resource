*** Settings ***
Library    Comm.py
Library    Power.py
Library    Image.py
Library    Util.py
Resource    ./image.resource

*** Keywords ***
File Should Exist
    [Arguments]    ${file}
    ${rc} =  Execute  ls -l ${file}
    Should Not Contain    ${rc}  No such file or directory  msg="File doesn't exist"

Setup Suite
    [Timeout]    45m
    [Arguments]    ${max_time}=30m
    ${image}=    Build Image    \    ${max_time}
    Should Not Be Empty    ${image}
    ${process}=    Power On    ${image}
    Connect    ${process}
    Login To Vm
    Sleep    30s    # Give the system some time to bring up network.

Teardown Suite
    [Timeout]    2m
    Shutdown Image
    Disconnect
    Power Off

Shutdown Image
    [Timeout]    2m
    ${command}=    Get Env    variable=EBCL_TC_SHUTDOWN_COMMAND    default=poweroff
    ${target}=    Get Env    variable=EBCL_TC_SHUTDOWN_TARGET    default=Power down
    log    Shutting down the image using ${command} and waiting for ${target}...
    Send Message    \n${command}
    Wait For Line    ${target}
    Sleep    1s
