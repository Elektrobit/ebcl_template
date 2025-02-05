*** Settings ***
Resource          resources/common.resource

Suite Setup    Setup Suite
Suite Teardown    Teardown Suite

Test Timeout      1m

Documentation  Appdev image tests.

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

*** Keywords ***

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
