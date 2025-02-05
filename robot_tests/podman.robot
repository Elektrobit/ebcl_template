*** Settings ***
Resource          resources/common.resource

Suite Setup    Setup Suite
Suite Teardown    Teardown Suite

Test Timeout      1m

Documentation  Appdev image tests.

*** Test Cases ***

Test Name Resolution
    Execute    ping -c 1 google.de

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
