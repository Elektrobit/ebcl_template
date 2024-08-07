*** Settings ***
Resource  ../common.resource
Suite Setup  Setup

Documentation  Test to check IPv6 address and status on eth0 in standard image

*** Test Cases ***
Check IPv6 settings on eth0
    ${ipv6_address}=    Execute    ip -6 addr show eth0| awk '/inet6/{print $2}'
    ${interface_status}=    Execute    ip link show eth0 | awk '/UP/{print $0}'

    Should contain    ${ipv6_address}    fd00::eb:2/64
    Should contain    ${interface_status}    UP

