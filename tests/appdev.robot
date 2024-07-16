*** Settings ***
Library    lib/Setup.py
Library    lib/Appdev.py
Suite Setup        Setup
Suite Teardown    Teardown
Keyword Tags    appdev    cmake

*** Test Cases ***

SDK shall support building cmake apps for aarch64
    [Tags]    fast
    Cmake App Aarch64

SDK shall support building cmake apps for x86_64
    [Tags]    fast
    Cmake App X86 64

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
