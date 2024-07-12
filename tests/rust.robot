*** Settings ***
Library    lib/Setup.py
Library    lib/Rust.py
Suite Setup        Setup
Suite Teardown    Teardown

*** Test Cases ***

SDK shall provide rustc
    Rustc Is Available

SDK shall provide cargo
    Cargo Is Available

*** Keywords ***
Setup
    Run Container

Teardown
    Stop Container
