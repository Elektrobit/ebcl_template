*** Settings ***
Resource    resources/image-build.robot

*** Test Cases ***
#==================================
# Tests for old format images
#==================================
Build Image example-old-images/qemu/berrymill
    [Tags]    amd64    qemu    berrymill    kiwi    ebcl    old
    [Timeout]    60m
    ${path}=    Set Variable    example-old-images/qemu/berrymill
    # ---------------
    # Build the image
    # ---------------
    ${full_path}=    Set Variable    /workspace/images/example-old-images/qemu/berrymill
    ${results_folder}=    Evaluate    $full_path + '/build'
    Connect
    # Remove old build artefacts - build from scratch
    Run Make    ${full_path}    clean    2m 
    # Build the image
    ${result}=    Execute    source /build/venv/bin/activate; cd ${full_path}; make image
    # Check for Embdgen log
    Should Contain    ${result}    Image was written to
    Sleep    1s
    # Check that image file exists
    ${file_info}=    Execute    cd ${results_folder}; file root.qcow2
    Should Not Contain    ${file_info}    No such file
    # Clear the output queue
    Clear Lines    
    Sleep    1s
    # -------------
    # Run the image
    # -------------
    Test That Make Does Not Rebuild    ${path}
    Run Image    ${path}
    Send Message    \ncrinit-ctl poweroff
    Sleep    20s
    Disconnect
