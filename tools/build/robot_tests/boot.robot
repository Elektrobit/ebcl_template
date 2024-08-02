*** Settings ***
Library  lib/Fakeroot.py
Library  lib/Boot.py
Suite Setup  Setup
Suite Teardown  Teardown

*** Test Cases ***
Kernel exists
    File Should Exist    /vmlinuz*

Config is OK
    File Should Exist    /config*
    Should Have Mode    /config*    777
    Should Be Owned By    /config*    123    456

Script was executed
    File Should Exist    /boot/some_config    regular empty file

*** Keywords ***
Setup
    Build Boot
    Load

Teardown
    Cleanup
