#!/bin/bash
#
# Copyright (c) Elektrobit Automotive GmbH. All rights reserved.
#
# ------------------------------------------------------------------------------
set -euo pipefail

SCRIPTDIR=$(dirname $(realpath "$0"))
WORKSPACE=$(dirname ${SCRIPTDIR})

# Default values
TESTS=$(find ${WORKSPACE} -name "*.robot" ! -name "images.robot")
EXCLUDE_TESTS="performance podman"
OUTPUT_DIR="output"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tests)
            TESTS="$2"
            shift 2
            ;;
        --exclude)
            EXCLUDE_TESTS="$2"
            shift 2
            ;;
        --outputdir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Assign basic test environment variables
source ${SCRIPTDIR}/ebcl_tf.env
# Assign test case environment variables
source ${SCRIPTDIR}/ebcl_tc_qemu_aarch64.env

EXCLUDE_ARGS=""
for exclude in ${EXCLUDE_TESTS}; do
    EXCLUDE_ARGS+=" --exclude ${exclude}"
done

ROBOT_CMDS="robot --outputdir ${WORKSPACE}/${OUTPUT_DIR} --loglevel TRACE --logtitle 'Robot Test' ${EXCLUDE_ARGS} ${TESTS}"
echo "Running command: ${ROBOT_CMDS}"
eval ${ROBOT_CMDS}
