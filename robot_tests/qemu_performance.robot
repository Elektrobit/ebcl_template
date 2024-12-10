*** Settings ***
Library    Image
Library    Performance    cycles=3
Test Timeout    30m

*** Variables ***
@{QEMU_CRINIT_PERFORMANCE_KEYWORDS}
...    qemu    Booting Linux
...    kernel_start    Linux version
...    early_userspace    init as init process
...    crinit_start    Crinit daemon version
...    first_service    command 0 of Task 'poweroff'
...    finish_poweroff    reboot: Power down

*** Test Cases ***

QEMU Performance Test For arm64/qemu/ebcl/crinit
    [Tags]    arm64    qemu    crinit    performance
    ${image}=    Build    path=arm64/qemu/ebcl/crinit    build_cmd=task build_performance_test
    Set Image    ${image}
    Set Measurement Points    ${QEMU_CRINIT_PERFORMANCE_KEYWORDS}
    Run Test    file=performance_arm64_qemu_crinit.txt
