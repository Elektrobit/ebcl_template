# Changelog for the EBcL VS Code workspace template


## Relesae 1.1.1 - 2024-04-25

Update for EBcL release 1.1.1.

Changes:
- Add pbuilder support
- Update to new apt repository structure


## Release 1.1 - 2024-03-29

Update for EBcL release 1.1.

Changes:
- added `apt` folder for embedded APT repository
- added `bin` folder for embedded workspace specific scripts
- changed `images` from "minimal image" to "example image" supporting SSH and apt.
- added new image examples for NXP RDB2 board
- aligned naming with QEMU and GCC: all former "amd64" is now "x86_64", if tooling allows, and all former "arm64" is now "aarch64". Please be aware that all apt and package related tooling still use "amd64" and "arm64".


## Release 1.0 - 2023-12-04

Initial Release of the EBcL template workspace.
