*** Settings ***
Resource  ../common.resource
Suite Setup  Setup

Documentation  Test to check IPv4 address and status on eth0 in standard image

*** Test Cases ***
Check IPv4 settings on eth0
    ${ipv4_address}=    Execute    ip -4 addr show eth0| awk '/inet/{print $2}'
    ${interface_status}=    Execute    ip -4 link show eth0 | awk '/UP/{print $0}'
    ${ipv4_gateway}=    Execute    ip -4 route | grep default | awk '{print $3}'

    Should contain    ${ipv4_address}    192.168.1.11/24
    Should contain    ${interface_status}    UP
    Should contain    ${ipv4_gateway}    192.168.1.1/24
