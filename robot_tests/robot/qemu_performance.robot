*** Settings ***
Library    Image
Library    Performance    cycles=3

Resource          resources/common.resource

Suite Setup    Setup

Test Timeout    30m

*** Keywords ***

Setup
    Set Env Qemu
    ${overlay}=    Build Test Overlay    build_target=build_performance    overlay_file=performance.squashfs
    Set Env    variable=EBCL_TC_IMAGE_KERNEL_CMDLINE_APPEND    value=test_overlay=/dev/vdb
    Set Env    variable=EBCL_TC_QEMU_ADDITIONAL_PARAMETERS    value=-drive format=raw,file=${overlay},if=virtio
    Setup Suite Without Login

*** Variables ***

@{QEMU_CRINIT_PERFORMANCE_KEYWORDS}
...    kernel_start    Linux version
...    early_userspace    init as init process
...    crinit_start    Crinit daemon version
...    first_service    command 0 of Task 'poweroff'
...    finish_poweroff    reboot: Power down

*** Test Cases ***

QEMU Performance Test crinit
    [Tags]    qemu    crinit    qemu-performance-crinit
    Set Measurement Points    ${QEMU_CRINIT_PERFORMANCE_KEYWORDS}
    Run Test
