*** Settings ***
Library  lib/Fakeroot.py
Library  lib/Boot.py
Suite Setup  Setup
Suite Teardown  Teardown

*** Test Cases ***
Systemd should exist
    File Should Exist    /usr/bin/systemd

Config was executed
    File Should Exist    /config

PreDisc was executed
    File Should Exist    /pre_disc_root

PostDisc was executed
    File Should Exist    /post_disc_root

*** Keywords ***
Setup
    Build Boot
    Load

Teardown
    Cleanup
