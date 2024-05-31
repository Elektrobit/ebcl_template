#!/bin/bash

VERSION="testing"

if [ ! -z $1 ]; then
    RUNNER=$1
else
    # docker or podman
    RUNNER="docker"
fi

echo "RUNNER: ${RUNNER}"

# prepare build result folder
mkdir -p /tmp/results/{images,packages} || true
RESULT_DIR=$(realpath /tmp/results)
echo "RESULT FOLDER: $RESULT_DIR"

SCRIPT=$(realpath "${BASH_SOURCE[0]}")
SCRIPT_DIR=$(dirname $SCRIPT)
echo "SCRIPT FOLDER: ${SCRIPT_DIR}"

# find workspace folder
WORKSPACE=$(realpath "$SCRIPT_DIR/..")
echo "WORKSPACE: $WORKSPACE"

# find images folder
IMAGES=$(realpath "$SCRIPT_DIR/../images")
echo "IMAGES: $IMAGES"

# find identity folder
IDENTITY=$(realpath "$SCRIPT_DIR/../identity")
echo "IDENTITY: $IDENTITY"

$RUNNER run --rm -it \
    -v ${HOME}/.ssh:/home/dev/.ssh:ro \
    -v ${RESULT_DIR}:/build/results:rw \
    -v ${WORKSPACE}:/workspace:rw \
    -v ${IMAGES}:/build/images:ro \
    -v ${IDENTITY}:/build/identity:ro \
    --privileged \
    linux.elektrobit.com/ebcl/sdk:testing