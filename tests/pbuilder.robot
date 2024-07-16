*** Settings ***
Library    lib/Setup.py
Library    lib/Pbuilder.py
Suite Setup        Setup
Suite Teardown    Teardown
Keyword Tags    pbuilder

*** Test Cases ***

SDK shall package config files
    [Tags]    slow
    Package Config Files

SDK shall package apps
    [Tags]    slow
    Package App    amd64
    Package App    arm64

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
