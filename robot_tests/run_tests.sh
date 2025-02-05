#!/bin/bash

function run_test_classes {
    echo "Running $# test classes $@ for image ${EBCL_TC_IMAGE}..."
    for TEST_CLASS in $@;
    do
        echo "Running test class ${TEST_CLASS} for image ${EBCL_TC_IMAGE}..."
        mkdir -p ${log_dir}/${EBCL_TC_IMAGE}/${TEST_CLASS}
        robot --outputdir ${log_dir}/${EBCL_TC_IMAGE}/${TEST_CLASS} ${TEST_CLASS}.robot
    done
}

if [ -n "$FORCE_CLEAN_REBUILD" ]; then
    echo "Enforcing image rebuild..."
    export SDK_ROBOT_SKIP_CLEAN="0"
else
    echo "Enforced image rebuild is off..."
fi

test_lib_folder=$(realpath ./lib)

export PYTHONPATH="${test_lib_folder}:${PYTHONPATH}"

if [ -f "test.env" ]; then
    source test.env
fi

rm -f output.xml
rm -f report.html
rm -f log.html
rm -f performance*.txt

robot --version
echo "PYTHONPATH: ${PYTHONPATH}"

current_date=$(date "+%Y-%m-%d-%H-%M-%S")
commit_id=$(git rev-parse HEAD)

report_archive="test_report_${current_date}_${commit_id}.zip"
log_dir="test_logs_${current_date}_${commit_id}"

mkdir -p ${log_dir}

if [[ $# -eq 0 ]] ; then
    export EBCL_TC_IMAGE="images"
    run_test_classes "images"

    export EBCL_TC_IMAGE="amd64/appdev/qemu/crinit"
    export EBCL_TC_SHUTDOWN_COMMAND="crinit-ctl poweroff"
    export EBCL_TC_SHUTDOWN_TARGET="Power down"

    run_test_classes "crinit" "docker" "podman"

    export EBCL_TC_IMAGE="arm64/appdev/qemu/crinit"

    run_test_classes "crinit" "docker" "podman"

    export EBCL_TC_IMAGE="amd64/appdev/qemu/systemd"
    export EBCL_TC_SHUTDOWN_COMMAND="systemctl poweroff"
    export EBCL_TC_SHUTDOWN_TARGET="System Power Off"

    run_test_classes "docker" "podman"

    export EBCL_TC_IMAGE="arm64/appdev/qemu/systemd"

    run_test_classes "docker" "podman"

    export EBCL_TC_IMAGE="images/arm64/qemu/ebcl"
    export EBCL_TC_SHUTDOWN_COMMAND="crinit-ctl poweroff"
    export EBCL_TC_SHUTDOWN_TARGET="Power down"

    run_test_classes "crinit" "docker"

    export EBCL_TC_IMAGE="images/arm64/qemu/jammy"
    export EBCL_TC_SHUTDOWN_COMMAND="systemctl poweroff"
    export EBCL_TC_SHUTDOWN_TARGET="System Power Off"

    run_test_classes "docker"

    export EBCL_TC_IMAGE="images/arm64/qemu/noble"

    run_test_classes "docker"

    export EBCL_TC_IMAGE="performance"
    run_test_classes "performance"

    # Generate merged report
    cd ${log_dir} ; rebot $(find . -name "output.xml") ; cd ..
else
    echo "Running robot with arguments: \"$@\""
    robot  --outputdir ${log_dir} "$@"
fi

for log in $(find ../images -type f -name "*.log" -not -path "*/extra/*" -not -path "*/user/*"); do
    copy=$(echo ${log:3} | tr / _)
    cp $log ${log_dir}/$copy
done


zip -r $report_archive ${log_dir}/* 1>/dev/null
rm -f images_*.log

rm -f report.html
rm -f log.html
rm -f output.xml

ln -sf ${log_dir}/report.html .
ln -sf ${log_dir}/log.html .
