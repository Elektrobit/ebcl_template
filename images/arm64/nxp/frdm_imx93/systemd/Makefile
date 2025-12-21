# Makefile for NXP iMX93 FRDM

variant = systemd
#-------------------------
# Additional configuration
#-------------------------
#Option Description Security Persistence Typical Use
#A	Entire rootfs in read-only dm-verity (no writes, no persistence)	✅ Highest	❌ None	Kiosk, critical IoT
#B	Rootfs in dm-verity, with overlayfs tmpfs upper (volatile writes only)	✅ High	❌ Volatile	Secure boot with ephemeral state
#C	Rootfs in dm-verity, with overlayfs persistent upper on /data	⚠️ Medium-high	✅ Persistent	Secure base OS + user updates
#D	Rootfs in dm-verity or dm-crypt, with authenticated/policy-controlled persistent layer (e.g., sealed key in TEE or secure enclave)
rootfs_design ?= patched_initrd_init_option_C
ifeq ($(rootfs_design), patched_initrd_init_option_C) # in this case there is a data partiotion encrypt it with key inside the OPTEE
full_optee ?= ../optee/optee.sh
endif

sysroot_filesystem_spec ?= sysroot.yaml
include ../frdm_imx93.mk
