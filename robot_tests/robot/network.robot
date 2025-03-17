*** Settings ***
Resource          resources/common.resource

Suite Setup    Setup
Suite Teardown    Teardown Suite

Test Timeout      1m

Documentation  Crinit specific image tests.

*** Keywords ***

Setup
    Set Env Qemu
    Setup Suite

*** Test Cases ***

Check IPv6 settings on eth0
    [Tags]    network    crinit    ipv6

    ${ipv6_status}=    Execute    ubus call network.interface.ipv6 status

    Should contain    ${ipv6_status}    "address": "fd00::eb:2"
    Should contain    ${ipv6_status}    "mask": 64
    Should contain    ${ipv6_status}    "up": true

Check IPv4 settings on lo
    [Tags]    network    crinit    ipv4    loopback
    
    ${loopback_status}=    Execute    ubus call network.interface.loopback status

    Should contain    ${loopback_status}    "address": "127.0.0.1"
    Should contain    ${loopback_status}    "up": true

Test Name Resolution
    [Tags]    name-resolution
    ${output}=    Execute    ping -c 1 google.de
    Should Contain    ${output}    icmp_seq=1
