*** Settings ***
Library    ../lib/Fakeroot.py
Library    ../lib/CommManager.py    mode=Process
Library    ../../.venv/lib/python3.10/site-packages/robot/libraries/String.py

*** Keywords ***
Run Make
    [Arguments]    ${path}    ${target}    ${max_time}=2h
    [Timeout]    ${max_time}
    ${result}=    Execute    source /build/venv/bin/activate; cd ${path}; make ${target}
    RETURN    ${result}

Build Image
    [Arguments]    ${path}    ${image}=image.raw    ${max_time}=1h
    [Timeout]    ${max_time}
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${results_folder}=    Evaluate    $full_path + '/build'
    
    # Remove old build artefacts - build from scratch
    Run Make    ${full_path}    clean    2m 

    # Build the initrd
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make initrd
    # Check for boot generator log
    Should Contain    ${result}    Image was written to

    Sleep    1s

    # Build the kernel
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make boot
    # Check for boot generator log
    Should Contain    ${result}    Results were written to

    Sleep    1s

    # Build the image
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make image
    # Check for Embdgen log
    Should Contain    ${result}    Writing image to

    Sleep    1s
    
    # Check that image file exists
    ${file_info}=    Execute    cd ${results_folder}; file ${image}
    Should Not Contain    ${file_info}    No such file
    
    # Clear the output queue
    Clear Lines    
    Sleep    1s

Test That Make Does Not Rebuild
    [Arguments]    ${path}
    [Timeout]    1m
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    ${output}=    Run Make    ${full_path}    image
    Should Contain    ${output}    Nothing to be done for 'image'

Run Image
    [Arguments]    ${path}
    [Timeout]    5m
    ${full_path}=    Evaluate    '/workspace/images/' + $path
    Send Message    source /build/venv/bin/activate; cd ${full_path}; make qemu
    ${success}=    Login To Vm
    Should Be True    ${success}

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
    Should Not Contain    ${systemd}    failed    ignore_case=${True}

Shutdown Systemd Image
    [Timeout]    2m
    Send Message    \nsystemctl poweroff
    Wait For Line Containing    System Power Off
    Sleep    1s

Test Systemd Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}
    Check For Startup Errors
    # TODO: Check For Systemd Unit Issues
    Shutdown Systemd Image
    Disconnect

Shutdown Crinit Image
    [Timeout]    2m
    Send Message    \ncrinit-ctl poweroff
    Wait For Line Containing    Power down
    Sleep    1s

Test Crinit Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}
    Check For Startup Errors
    Check For Startup Fails
    Check For Crinit Task Issues
    Shutdown Crinit Image
    Disconnect

Test Hardware Image
    [Arguments]    ${path}    ${image}=image.raw
    Connect
    Build Image    ${path}    ${image}
    Test That Make Does Not Rebuild    ${path}
