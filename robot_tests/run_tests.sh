#!/bin/bash

function run_test_classes {
    echo "Running $# test classes $@ for image ${EBCL_TC_IMAGE}..."
    for TEST_CLASS in $@;
    do
        echo "Running test class ${TEST_CLASS} for image ${EBCL_TC_IMAGE}..."
        mkdir -p ${log_dir}/${EBCL_TC_IMAGE}/${TEST_CLASS}
        robot ${EBCL_TC_ROBOT_PARAMS} --outputdir ${log_dir}/${EBCL_TC_IMAGE}/${TEST_CLASS} ${TEST_CLASS}.robot
        return_code=$(($return_code + $?))
        echo "Test ${TEST_CLASS} for image ${EBCL_TC_IMAGE} executed. Return code: ${return_code}"
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

export return_code=0

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
    for TEST_ENV in $(find . -name "*.test.env");
    do
        source ${TEST_ENV}
        run_test_classes ${EBCL_TC_ROBOT_FILES}
        # Reset robot flags
        export EBCL_TC_ROBOT_PARAMS=""
    done

    # Generate merged report
    cd ${log_dir} ; rebot $(find . -name "output.xml") ; cd ..
else
    if [[ $1 == *.test.env ]]
    then
        for test in $@; do
            echo "Running test env: $1"
            source $1
            run_test_classes ${EBCL_TC_ROBOT_FILES}
            # Reset robot flags
            export EBCL_TC_ROBOT_PARAMS=""
        done
    else
        echo "Running robot with arguments: \"$@\""
        robot  --outputdir ${log_dir} "$@"
        return_code=$(($return_code + $?))
    fi

    # Generate merged report
    cd ${log_dir} ; rebot $(find . -name "output.xml") ; cd ..
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

echo "Tests executed. Overall return code: ${return_code}"

exit $return_code