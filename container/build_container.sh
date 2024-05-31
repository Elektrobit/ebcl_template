#!/bin/bash

VERSION="testing"
BASE_NAME="sdk"
REPO="linux.elektrobit.com/ebcl"
BASE_CONTAINER_NAME="ubuntu:22.04"

if [ ! -z $1 ]; then
    BUILDER=$1
else
    # docker or podman
    BUILDER="docker"
fi

echo "BUILDER: ${RUNNER}"

function build_container() {
    $BUILDER build \
        -t ${CONTAINER_NAME} \
        --build-arg BASE_CONTAINER_NAME="${BASE_CONTAINER_NAME}" \
        ${FOLDER}
}

export BASE_CONTAINER_NAME

FOLDERS="base pbuilder"

for FOLDER in $FOLDERS; do
    CONTAINER_NAME="${REPO}/${BASE_NAME}_${FOLDER}:${VERSION}"
    build_container
    BASE_CONTAINER_NAME="$REPO/${BASE_NAME}_${FOLDER}:${VERSION}"
done

$BUILDER tag ${BASE_CONTAINER_NAME} "${REPO}/${BASE_NAME}:${VERSION}"
