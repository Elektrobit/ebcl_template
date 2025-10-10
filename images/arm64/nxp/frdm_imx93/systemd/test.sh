#!/bin/sh
##testing dm-verity using dmsetup on host
BLUE='\033[0;34m' # result
NC='\033[0m' # No Color

SECTORS=$1
BLOCK_SIZE=$2
DATA_BLOCKS=$3
HASH_START=$4
ROOT_HASH=$5
SALT=$6

echo "${BLUE}dm-verity params:${NC}"
echo "${BLUE}  SECTORS=${SECTORS}${NC}"
echo "${BLUE}  BLOCK_SIZE=${BLOCK_SIZE}${NC}"
echo "${BLUE}  DATA_BLOCKS=${DATA_BLOCKS}${NC}"
echo "${BLUE}  HASH_START=${HASH_START}${NC}"
echo "${BLUE}  ROOT_HASH=${ROOT_HASH}${NC}"
echo "${BLUE}  SALT=${SALT}${NC}"

echo "${BLUE}sudo losetup -D${NC}"
sudo losetup -D
echo "${BLUE}LOOP=$(sudo losetup -f --show -P build/image.raw)${NC}"
LOOP=$(sudo losetup -f --show -P build/image.raw)
echo "${BLUE}ls -l ${LOOP}*${NC}"
ls -l ${LOOP}*
# see whether the hash partition starts with 'verity' (superblock):
echo "${BLUE}sudo dd if=${LOOP}p3 bs=4096 count=1 | hexdump -C | sed -n '1,8p'${NC}"
sudo dd if=${LOOP}p3 bs=4096 count=1 | hexdump -C | sed -n '1,8p'

# if you have the header, dump it:
echo "${BLUE}sudo veritysetup dump ${LOOP}p3${NC}"
sudo veritysetup dump ${LOOP}p3

# verify with veritysetup (use bytes):
HASH_OFFSET_BYTES=$(( HASH_START * BLOCK_SIZE ))
echo "${BLUE}sudo veritysetup verify --hash-offset=$HASH_OFFSET_BYTES --data-blocks=$DATA_BLOCKS --data-block-size=$BLOCK_SIZE --hash-block-size=$BLOCK_SIZE --salt=$SALT ${LOOP}p2 ${LOOP}p3 $ROOT_HASH${NC}"

sudo veritysetup verify --hash-offset=$HASH_OFFSET_BYTES \
  --data-blocks=$DATA_BLOCKS --data-block-size=$BLOCK_SIZE \
  --hash-block-size=$BLOCK_SIZE --salt=$SALT \
  ${LOOP}p2 ${LOOP}p3 $ROOT_HASH

# test kernel mapping via dmsetup (hash_start is in blocks):
echo "${BLUE}sudo dmsetup remove rootfs || true${NC}"
sudo dmsetup remove rootfs || true
echo "${BLUE}sudo dmsetup create rootfs --readonly --table \"0 ${SECTORS} verity 1 ${LOOP}p2 ${LOOP}p3 ${BLOCK_SIZE} ${BLOCK_SIZE} ${DATA_BLOCKS} 1 sha256 ${ROOT_HASH} ${SALT}\"${NC}"
sudo dmsetup create rootfs --readonly --table \
"0 ${SECTORS} verity 1 ${LOOP}p2 ${LOOP}p3 ${BLOCK_SIZE} ${BLOCK_SIZE} ${DATA_BLOCKS} 1 sha256 ${ROOT_HASH} ${SALT}"
echo "${BLUE}dmsetup create ... DONE${NC}"
sleep 1
# check device and try to mount:
echo "${BLUE}ls -l /dev/mapper/rootfs${NC}"
ls -l /dev/mapper/rootfs
echo "${BLUE}sudo mount -o ro /dev/mapper/rootfs /mnt/test || dmesg | tail -n 40${NC}"
sudo mount -o ro /dev/mapper/rootfs /mnt/test || dmesg | tail -n 40
ls -la /mnt/test
sudo umount /mnt/test/
sudo dmsetup remove rootfs || true
sudo losetup -D
