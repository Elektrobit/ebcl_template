echo "Running signed bootscr from FIT..."
setenv rootdev "/dev/mmcblk1p2"
setenv bootargs "console=ttyLP0,115200 root=${rootdev} rootwait rw"
bootm 0x90000000#conf
