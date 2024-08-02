*** Settings ***
Library    lib/Base.py
Library    lib/Setup.py
Suite Setup        Setup
Suite Teardown    Teardown
Keyword Tags    base

*** Test Cases ***

SDK version shall be 1.2
    [Tags]    fast
    Sdk Version    1.2

SDK user shall be ebcl
    [Tags]    fast
    Ensure Ebcl User Is Used

SDK shall provide a proper Debian environment
    [Tags]    fast
    Ensure Environment Is Ok

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
