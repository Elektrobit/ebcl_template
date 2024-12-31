#!/bin/bash

#Requires:
sudo apt update
sudo apt install bc bison flex libssl-dev u-boot-tools python3-pycryptodome python3-pyelftools binutils-arm-linux-gnueabihf binutils-aarch64-linux-gnu gcc-arm-linux-gnueabihf gcc-aarch64-linux-gnu tree

DIR="$PWD"
target_dir="$1/deploy"
mkdir -p $target_dir

if [ -d "$target_dir/tmp/ti-linux-firmware/" ] ; then
	rm -rf $target_dir/tmp/ti-linux-firmware/ || true
fi

if [ ! -f "$target_dir/ipc_echo_testb_mcu1_0_release_strip.xer5f" ] ; then
	mkdir -p $target_dir/tmp/ti-linux-firmware/
	git clone -b 10.00.08 https://git.ti.com/git/processor-firmware/ti-linux-firmware.git --depth=1 $target_dir/tmp/ti-linux-firmware/
#	git clone -b 08.03.00.003 https://git.ti.com/git/processor-firmware/ti-linux-firmware.git --depth=1 $target_dir/tmp/ti-linux-firmware/
	cp -v $target_dir/tmp/ti-linux-firmware/ti-dm/j721e/ipc_echo_testb_mcu1_0_release_strip.xer5f $target_dir/
fi

if [ -d "$target_dir/tmp/arm-trusted-firmware/" ] ; then
	rm -rf $target_dir/tmp/arm-trusted-firmware/ || true
fi

if [ ! -f "$target_dir/bl31.bin" ] ; then
	mkdir -p $target_dir/tmp/arm-trusted-firmware/
	git clone -b bbb.io-08.01.00.006 https://git.beagleboard.org/beagleboard/arm-trusted-firmware.git --depth=1 $target_dir/tmp/arm-trusted-firmware/
#	git clone -b bbb.io-08.01.00.006 https://git.beagleboard.org/beagleboard/arm-trusted-firmware.git --depth=1 $target_dir/tmp/arm-trusted-firmware/
	make -C $target_dir/tmp/arm-trusted-firmware -j4 CROSS_COMPILE=aarch64-linux-gnu- CFLAGS= LDFLAGS= ARCH=aarch64 PLAT=k3 TARGET_BOARD=generic SPD=opteed all
	cp -v $target_dir/tmp/arm-trusted-firmware/build/k3/generic/release/bl31.bin $target_dir/
fi

if [ -d "$target_dir/tmp/optee_os/" ] ; then
	rm -rf $target_dir/tmp/optee_os/ || true
fi

if [ ! -f "$target_dir/tee-pager_v2.bin" ] ; then
	mkdir -p $target_dir/tmp/optee_os/
	git clone -b bb.io-08.01.00.005 https://git.beagleboard.org/beagleboard/optee_os.git --depth=1 $target_dir/tmp/optee_os/
#	git clone -b 08.01.00.005 https://git.beagleboard.org/beagleboard/optee_os.git --depth=1 $target_dir/tmp/optee_os/
	make -C $target_dir/tmp/optee_os -j4 CFLAGS= LDFLAGS= PLATFORM=k3-j721e CFG_ARM64_core=y
	cp -v $target_dir/tmp/optee_os/out/arm-plat-k3/core/tee-pager_v2.bin $target_dir/
fi

if [ -d "$target_dir/tmp/k3-image-gen" ] ; then
	rm -rf $target_dir/tmp/k3-image-gen || true
fi

if [ ! -f "$target_dir/sysfw.itb" ] ; then
	mkdir -p $target_dir/tmp/k3-image-gen/
    git clone -b 09.00.00.001 https://github.com/beagleboard/k3-image-gen --depth=1 $target_dir/tmp/k3-image-gen/
#	git clone -b 08.01.00.006 https://github.com/beagleboard/k3-image-gen --depth=1 $target_dir/tmp/k3-image-gen/
	make -C $target_dir/tmp/k3-image-gen/ SOC=j721e CONFIG=evm CROSS_COMPILE=arm-linux-gnueabihf-
	cp -v $target_dir/tmp/k3-image-gen/sysfw.itb $target_dir/
fi


if [ -d "$target_dir/tmp/u-boot/" ] ; then
	rm -rf $target_dir/tmp/u-boot/ || true
fi


if [ ! -f "$target_dir/u-boot.img" ] ; then
	mkdir -p $target_dir/tmp/u-boot/
	git clone -b v2024.07 https://git.beagleboard.org/beagleboard/u-boot.git --depth=1 $target_dir/tmp/u-boot/
#	git clone -b v2021.01-ti-08.01.00.006 https://git.beagleboard.org/beagleboard/u-boot.git --depth=1 $target_dir/tmp/u-boot/

	if [ ! -f "$target_dir/tiboot3.bin" ] ; then
		make -C $target_dir/tmp/u-boot -j1 O=../r5 ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- j721e_evm_r5_defconfig
		make -C $target_dir/tmp/u-boot -j5 O=../r5 ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-
		cp -v $target_dir/tmp/r5/tiboot3.bin $target_dir/
	fi

	make -C $target_dir/tmp/u-boot -j1 O=../a72 ARCH=arm CROSS_COMPILE=aarch64-linux-gnu- j721e_evm_a72_defconfig
	make -C $target_dir/tmp/u-boot -j5 O=../a72 ARCH=arm CROSS_COMPILE=aarch64-linux-gnu- ATF=${DIR}/$target_dir/bl31.bin TEE=${DIR}/$target_dir/tee-pager_v2.bin DM=${DIR}/$target_dir/ipc_echo_testb_mcu1_0_release_strip.xer5f
	cp -v $target_dir/tmp/a72/tispl.bin $target_dir/
	cp -v $target_dir/tmp/a72/u-boot.img $target_dir/
fi

tree $target_dir/
