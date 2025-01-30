*** Settings ***
Resource          resources/common.resource

Suite Setup    Setup Suite    arm64/appdev/qemu/systemd
Suite Teardown    Teardown Suite Systemd

Test Timeout      1m

Documentation  QEMU arm64 systemd appdev image tests.

*** Test Cases ***

Test Name Resolution
    Execute    ping -c 1 google.de

Test Ubuntu Docker Image
    [Tags]    qemu    appdev    crinit    docker
    [Timeout]    5m
    Docker Daemon Is Running
    Pull Docker Image    ubuntu
    Run Docker Container    ubuntu    ub24
    Stop Docker Container   ub24
    Remove Docker Container   ub24

Test Busybox Podman Image
    [Tags]    qemu    appdev    crinit    podman
    [Timeout]    5m
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
