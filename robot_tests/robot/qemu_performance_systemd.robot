*** Settings ***
Library    Image
Library    Performance    cycles=3

Resource          resources/common.resource

Suite Setup    Setup

Test Timeout    30m

*** Keywords ***

Setup
    Set Env Qemu
    ${overlay}=    Build Test Overlay    build_target=build_performance_systemd    overlay_file=performance_systemd.squashfs
    Set Env    variable=EBCL_TC_IMAGE_KERNEL_CMDLINE_APPEND    value=test_overlay=/dev/vdb
    Set Env    variable=EBCL_TC_QEMU_ADDITIONAL_PARAMETERS    value=-drive format=raw,file=${overlay},if=virtio
    Setup Suite Without Login

*** Variables ***

@{QEMU_SYSTEMD_PERFORMANCE_KEYWORDS}
...    kernel_start    Linux version
...    early_userspace    init as init process
...    systemd_start    running in system mode
...    first_service    Started.*Extension point for tests
...    finish_poweroff    reboot: Power down

*** Test Cases ***

QEMU Performance Test systemd
    [Tags]    arm64    qemu    systemd    qemu-performance-systemd
    Set Measurement Points    ${QEMU_SYSTEMD_PERFORMANCE_KEYWORDS}
    Run Test
