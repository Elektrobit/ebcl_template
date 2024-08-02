*** Settings ***
Library    lib/Setup.py
Library    lib/Rust.py
Suite Setup        Setup
Suite Teardown    Teardown
Keyword Tags    rust

*** Test Cases ***

SDK shall provide rustc
    [Tags]    fast
    Rustc Is Available

SDK shall provide cargo
    [Tags]    fast
    Cargo Is Available

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
