#!/bin/sh
set -e
echo "preparing rootfs for dm-verity"

# === Paths ===
ROOT_TAR="build/root.config.tar"
ROOT_IMG="build/root.ext4"
HASH_FILE="${ROOT_IMG}.hash"
VERITY_INFO="build/verity.info"
BOOT_CMD="build/boot.cmd"
ROOT_VERITY_IMG="build/root-verity.ext4"

IMG_SIZE_MB=1024

mkdir -p build/rootfs build/mnt

echo "Extracting rootfs..."
tar -xf "${ROOT_TAR}" -C build/rootfs

echo "Creating empty ext4 image ${ROOT_IMG} (${IMG_SIZE_MB}MB)..."
dd if=/dev/zero of="${ROOT_IMG}" bs=1M count=${IMG_SIZE_MB}
mkfs.ext4 -F "${ROOT_IMG}"

echo "Populating image..."
sudo mount -o loop "${ROOT_IMG}" build/mnt
sudo cp -a build/rootfs/* build/mnt/
sync
sudo umount build/mnt

# === Generate salt ===
SALT=$(xxd -p -l 32 /dev/urandom | tr -d '\n')

echo "Running veritysetup format with salt (writing hash tree to ${HASH_FILE})..."
veritysetup format --salt="${SALT}" "${ROOT_IMG}" "${HASH_FILE}" 2>&1 | tee "${VERITY_INFO}"

# === Parse verity output ===
ROOT_HASH=$(grep -i '^Root hash:' "${VERITY_INFO}" | awk '{print $3}')
DATA_BLOCKS=$(grep -i '^Data blocks:' "${VERITY_INFO}" | awk '{print $3}')
BLOCK_SIZE=$(grep -i '^Data block size:' "${VERITY_INFO}" | awk '{print $4}')
HASH_START=$(grep -i '^Hash start:' "${VERITY_INFO}" | awk '{print $3}' || true)

#HASH_START="${DATA_BLOCKS}"
HASH_START=1 # start from 0 as it is seprate partition

if [ -z "${ROOT_HASH}" ] || [ -z "${DATA_BLOCKS}" ] || [ -z "${BLOCK_SIZE}" ]; then
  echo "Failed to parse verity output (${VERITY_INFO})."
  sed -n '1,200p' "${VERITY_INFO}"
  exit 1
fi

# Device-mapper 'sectors' = data_blocks * (block_size / 512)
SECTORS=$(( DATA_BLOCKS * (BLOCK_SIZE / 512) ))

echo "Parsed verity values:"
echo "  ROOT_HASH=${ROOT_HASH}"
echo "  DATA_BLOCKS=${DATA_BLOCKS}"
echo "  BLOCK_SIZE=${BLOCK_SIZE}"
echo "  HASH_START=${HASH_START}"
echo "  SECTORS=${SECTORS}"
echo "  SALT=${SALT}"

# === Write boot.cmd ===
cat > "${BOOT_CMD}" <<EOF
echo "Running signed bootscr from FIT..."
#setenv dm_verity "rootfs,,0,ro,0 ${SECTORS} verity 1 /dev/mmcblk1p2 /dev/mmcblk1p2 ${BLOCK_SIZE} ${BLOCK_SIZE} ${DATA_BLOCKS} ${HASH_START} sha256 ${ROOT_HASH} ${SALT}"
#setenv bootargs "console=ttyLP0,115200 root=/dev/dm-0 rootwait ro dm-mod.create=\"\${dm_verity}\""
setenv bootargs "console=ttyLP0,115200 root=/dev/dm-0 ro \
  verity.sectors=${SECTORS} \
  verity.blksize=${BLOCK_SIZE} \
  verity.datablocks=${DATA_BLOCKS} \
  verity.hashstart=${HASH_START} \
  verity.roothash=${ROOT_HASH} \
  verity.salt=${SALT}"
bootm 0x90000000#conf
EOF

echo "Created ${BOOT_CMD}"
cat "${BOOT_CMD}"

# === Combine data + hash into final image ===
#cat "${ROOT_IMG}" "${HASH_FILE}" > "${ROOT_VERITY_IMG}"
#sync

echo "Wrote ${BOOT_CMD} and ${ROOT_VERITY_IMG}"
