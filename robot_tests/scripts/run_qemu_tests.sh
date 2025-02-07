#!/bin/bash
#
# Copyright (c) Elektrobit Automotive GmbH. All rights reserved.
#
# ------------------------------------------------------------------------------
set -euo pipefail

SCRIPTDIR=$(dirname $(realpath "$0"))
WORKSPACE=$(dirname ${SCRIPTDIR})

# assign default values if it is not done by the calling script
source ${SCRIPTDIR}/ebcl_env.sh

echo "Starting qemu"

#echo "Wait 20sec for the bart system to boot"
#sleep 20

echo "Running robot tests from ${WORKSPACE}"
robot  --outputdir ${WORKSPACE}/output --loglevel TRACE --logtitle "Robot Test" ${WORKSPACE}/crinit.robot
