*** Settings ***
Library    Comm.py
Library    Power.py
Library    Image.py
Library    Util.py
Library    robot/libraries/String.py

*** Keywords ***
Build Image
    [Arguments]    ${path}=    ${max_time}=15m
    [Timeout]    ${max_time}
    Clear    ${path}
    ${image}=    Build    ${path}
    Should Not Be Empty    ${image}
    RETURN    ${image}

Check For Startup Errors
    [Timeout]    2m
    # Filter known log containing the error search word.
    ${kernel_logs}=    Execute    dmesg
    ${kernel_logs}=    Replace String    ${kernel_logs}    Correctable Errors collector initialized    \
    Should Not Contain    ${kernel_logs}    error    ignore_case=${True}

Check For Startup Fails
    [Timeout]    2m
    ${kernel_logs}=    Execute    dmesg
    Should Not Contain    ${kernel_logs}    failed    ignore_case=${True}

Check For Crinit Task Issues
    [Timeout]    2m
    ${crinit}=    Execute    crinit-ctl list
    Should Not Contain    ${crinit}    failed    ignore_case=${True}
    Should Not Contain    ${crinit}    wait    ignore_case=${True}

Check For Systemd Unit Issues
    [Timeout]    2m
    ${systemd}=    Execute    systemctl list-units --no-pager
    ${systemd}=    Filter Lines Containing    lines=${systemd}    search=binfmt
    Should Not Contain    ${systemd}    failed    ignore_case=${True}

Shutdown Systemd Image
    [Timeout]    2m
    Send Message    \nsystemctl poweroff
    Wait For Line    System Power Off
    Sleep    1s

Test Systemd Image
    [Arguments]    ${path}
    ${image}=    Build Image    ${path}
    Should Not Be Empty    ${image}
    ${process}=    Power On    ${image}
    Connect    ${process}
    Login To Vm
    Check For Startup Errors
    Check For Systemd Unit Issues
    Shutdown Systemd Image
    Disconnect

Shutdown Crinit Image
    [Timeout]    2m
    Send Message    \ncrinit-ctl poweroff
    Wait For Line    Power down
    Sleep    1s

Test Crinit Image
    [Arguments]    ${path}
    ${image}=    Build Image    ${path}
    Should Not Be Empty    ${image}
    ${process}=    Power On    ${image}
    Connect    ${process}
    Login To Vm
    Check For Startup Errors
    Check For Startup Fails
    Check For Crinit Task Issues
    Shutdown Crinit Image
    Disconnect

Test Hardware Image
    [Arguments]    ${path}    ${build_timeout}=15m
    ${image}=    Build Image    ${path}    max_time=${build_timeout}
    Should Not Be Empty    ${image}
