*** Settings ***
Library    lib/Setup.py
Library    lib/Pbuilder.py
Suite Setup        Setup
Suite Teardown    Teardown

*** Test Cases ***

SDK shall package config files
    Package Config Files

SDK shall package apps
    Package App    amd64
    Package App    arm64

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
