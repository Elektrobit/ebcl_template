*** Settings ***
Resource          resources/common.resource

Suite Setup    Setup Suite    arm64/appdev/qemu/crinit
Suite Teardown    Teardown Suite

Test Timeout      1m

Documentation  QEMU crinit appdev image tests.

*** Test Cases ***

Check IPv6 settings on eth0
    [Tags]    qemu    appdev    crinit    ipv6

    ${ipv6_status}=    Execute    ubus call network.interface.ipv6 status

    Should contain    ${ipv6_status}    "address": "fd00::eb:2"
    Should contain    ${ipv6_status}    "mask": 64
    Should contain    ${ipv6_status}    "up": true

Check IPv4 settings on lo
    [Tags]    qemu    appdev    crinit    ipv4    loopback
    
    ${loopback_status}=    Execute    ubus call network.interface.loopback status

    Should contain    ${loopback_status}    "address": "127.0.0.1"
    Should contain    ${loopback_status}    "up": true

Test Name Resolution
    Sleep    30s    # Give the system some time to bring up network.
    Execute    ping -c 1 google.de

Test Ubuntu Docker Image
    [Tags]    qemu    appdev    crinit    docker
    [Timeout]    5m
    Sleep    30s    # Give the system some time to bring up network.
    Docker Daemon Is Running
    Pull Docker Image    ubuntu
    Run Docker Container    ubuntu    ub24
    Stop Docker Container   ub24
    Remove Docker Container   ub24

Test Busybox Podman Image
    [Tags]    qemu    appdev    crinit    podman
    [Timeout]    5m
    Sleep    30s    # Give the system some time to bring up network.
    Pull Podman Image    busybox
    Run Podman Container    busybox    bb24
    Stop Podman Container   bb24
    Remove Podman Container   bb24

*** Keywords ***

Should Contain Podman Graphroot Dir
    [Arguments]    ${location}
    ${podman_loc}=    Execute    \ncat /etc/containers/storage.conf
    Should Contain  ${podman_loc}    graphroot = \"${location}\"

Pull Podman Image
    [Arguments]    ${image}
    Execute    \npodman pull ${image}
    ${image_ls}=   Execute    \npodman images
    Should Contain   ${image_ls}    ${image}
    Sleep    1s

Run Podman Container
    [Arguments]    ${image}    ${cont_name}
    Execute    \npodman rm ${cont_name}
    Execute    \npodman run -it -d --name ${cont_name} ${image}
    ${cont_id}=   Execute    \npodman ps --format \"\{\{.Names\}\}\"
    Should Contain    ${cont_id}    ${cont_name}

Stop Podman Container
    [Arguments]    ${cont}
    [Timeout]    2m
    Execute    \npodman stop ${cont}
    Sleep    5s
    ${cont_ls}=   Execute    \npodman ps -a --format \"\{\{.Status\}\}\"
    Should Contain   ${cont_ls}    Exited

Remove Podman Container
    [Arguments]    ${cont}
    Execute    \npodman rm ${cont}
    ${cont_ls}=   Execute    \npodman container ls
    Should Not Contain   ${cont_ls}  ${cont}

Docker Daemon Is Running
    ${dockerd_ls}=    Execute    ls /run/docker.sock
    Should Not Contain    ${dockerd_ls}    No such file or directory

Should Contain Docker Root Dir
    [Arguments]    ${location}
    [Timeout]    1m
    ${docker_loc}=    Execute    \ndocker info
    Should Contain  ${docker_loc}    Docker Root Dir\: ${location}

Pull Docker Image
    [Arguments]    ${image}
    Execute    docker pull ${image}
    ${image_ls}=   Execute    docker images
    Should Contain   ${image_ls}    ${image}

Run Docker Container
    [Arguments]    ${image}    ${cont_name}
    Execute    docker rm ${cont_name}
    Execute    docker run -it -d --name ${cont_name} ${image}
    ${cont_id}=   Execute    \ndocker ps
    Should Contain    ${cont_id}    ${cont_name}

Stop Docker Container
    [Arguments]    ${cont}
    Execute    docker stop ${cont}
    Sleep    20s
    ${cont_ls}=   Execute    \ndocker ps -a
    Should Contain   ${cont_ls}    Exited

Remove Docker Container
    [Arguments]    ${cont}
    Execute    \ndocker rm ${cont}
    ${cont_ls}=   Execute    \ndocker container ls
    Should Not Contain   ${cont_ls}  ${cont}
