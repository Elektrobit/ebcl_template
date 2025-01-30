*** Settings ***
Library    Comm.py
Library    Power.py
Library    Image.py    image_base=/workspace/images
Library    Util.py
Resource    ./image.resource

*** Keywords ***
File Should Exist
    [Arguments]    ${file}
    ${rc} =  Execute  ls -l ${file}
    Should Not Contain    ${rc}  No such file or directory  msg="File doesn't exist"

Setup Suite
    [Arguments]    ${path}
    [Timeout]    15m
    ${image}=    Build Image    ${path}
    Should Not Be Empty    ${image}
    ${process}=    Power On    ${image}
    Connect    ${process}
    Login To Vm

Teardown Suite
    [Timeout]    2m
    Shutdown Crinit Image
    Disconnect
    Power Off

Teardown Suite Systemd
    [Timeout]    2m
    Shutdown Systemd Image
    Disconnect
    Power Off
