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

@{QEMU_SYSTEMD_PERFORMANCE_KEYWORDS}
...    qemu    Booting Linux
...    kernel_start    Linux version
...    early_userspace    init as init process
...    systemd_start    running in system mode
...    first_service    Started.*Extension point for tests
...    finish_poweroff    reboot: Power down

*** Test Cases ***

QEMU Performance Test For arm64/qemu/ebcl/crinit
    [Tags]    arm64    qemu    crinit    performance
    Skip    Test overlay concept requires rework.
    ${image}=    Build    path=arm64/qemu/ebcl/crinit    build_cmd=task build_performance_test
    Set Image    ${image}
    Set Measurement Points    ${QEMU_CRINIT_PERFORMANCE_KEYWORDS}
    Run Test    file=performance_arm64_qemu_crinit.txt

QEMU Performance Test For arm64/qemu/ebcl/systemd
    [Tags]    arm64    qemu    systemd    performance
    Skip    Test overlay concept requires rework.
    ${image}=    Build    path=arm64/qemu/ebcl/systemd    build_cmd=task build_performance_test_systemd
    Set Image    ${image}
    Set Measurement Points    ${QEMU_SYSTEMD_PERFORMANCE_KEYWORDS}
    Run Test    file=performance_arm64_qemu_systemd.txt    run_cmd=task run_performance_test_systemd
