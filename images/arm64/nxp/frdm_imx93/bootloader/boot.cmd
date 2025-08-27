setenv bootargs console=ttyLP0,115200 root=/dev/mmcblk1p2 rootwait rw
fatload mmc 1:1 0x90000000 fit.itb
bootm 0x90000000