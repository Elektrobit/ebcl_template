*** Settings ***
Library  lib/Build.py
Keyword Tags    build    container

*** Test Cases ***

Containers shall build
    [Tags]    slow
    Build Containers
