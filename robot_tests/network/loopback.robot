*** Settings ***
Resource  ../common.resource
Suite Setup  Setup

Documentation  Test to check loopback device address and status in the standard EBCL image

*** Test Cases ***
Check IPv4 settings on lo
    ${ipv4_address}=    Execute    ip -4 addr show lo | awk '/inet/{print $2}'
    ${interface_status}=    Execute    ip -4 link show lo | awk '/UP/{print $0}'

    Should contain    ${ipv4_address}    127.0.0.1
    Should contain    ${interface_status}    UP
