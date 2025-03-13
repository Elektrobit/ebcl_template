#!/bin/bash

function run_tests {
    if [ -z ${EBCL_TC_IMAGE+x} ]; then
        echo "Test env file $1 is invalid, the parameter EBCL_TC_IMAGE is missing!"
        exit 1
    fi

    if [ -z ${EBCL_TC_ROBOT_TAGS+x} ]; then
        # Some tests require specific env paramters. Running all tests at one makes no sense.
        echo "Test env file $1 is invalid, the parameter EBCL_TC_ROBOT_TAGS is missing!"
        exit 1
    fi

    if [ -z ${EBCL_IMAGE_TYPE+x} ]; then
        echo "No image type defined."
    fi

    if [ -z ${EBCL_IMAGE_ARCH+x} ]; then
        echo "No image arch defined!"
    fi

    if [ -z ${EBCL_TC_ROBOT_FILES+x} ]; then
        echo "Using all avaiable robot files."
        EBCL_TC_ROBOT_FILES="*.robot"
    else
        EBCL_TC_ROBOT_FILES=$(echo ${EBCL_TC_ROBOT_TAGS} | tr " " " ${TEST_ROBOT_FOLDER}/")
        echo "Using only robot file ${EBCL_TC_ROBOT_FILES}."
    fi

    if [ -z ${EBCL_TF_TEST_OVERLAY_FOLDER+x} ]; then
        TEST_OVERLAY_FOLDER="--variable TEST_OVERLAY_FOLDER:${EBCL_TF_TEST_OVERLAY_FOLDER}"
        echo "Using test overlay folder: ${EBCL_TF_TEST_OVERLAY_FOLDER}"
    else
        TEST_OVERLAY_FOLDER=""
    fi

    TAGS=$(echo ${EBCL_TC_ROBOT_TAGS} | sed -r 's/ / -i /g')

    echo "Running tests with tags ${EBCL_TC_ROBOT_TAGS} for image ${EBCL_TC_IMAGE} (type=${EBCL_IMAGE_TYPE}, arch=${EBCL_IMAGE_ARCH})..."
    mkdir -p ${log_dir}/${EBCL_TC_IMAGE}
    robot ${EBCL_TC_ROBOT_PARAMS} -i $TAGS ${TEST_OVERLAY_FOLDER} --variable IMAGE_TYPE:${EBCL_IMAGE_TYPE} --variable IMAGE_ARCH:${EBCL_IMAGE_ARCH}  --outputdir ${log_dir}/${EBCL_TC_IMAGE} ${TEST_ROBOT_FOLDER}/${EBCL_TC_ROBOT_FILE}
    EXIT_CODE=$((EXIT_CODE+$?))
    echo "Overall exit code: ${EXIT_CODE}"
}

if [ -n "$FORCE_CLEAN_REBUILD" ]; then
    echo "Enforcing image rebuild..."
    export SDK_ROBOT_SKIP_CLEAN="0"
else
    echo "Enforced image rebuild is off..."
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TEST_LIB_FOLDER=$(realpath ${SCRIPT_DIR}/lib)
TEST_ROBOT_FOLDER=$(realpath ${SCRIPT_DIR}/robot)
TEST_ENV_FOLDER=$(realpath ${SCRIPT_DIR}/image.env)

cd $SCRIPT_DIR

export PYTHONPATH="${TEST_LIB_FOLDER}:${TEST_ROBOT_FOLDER}:${PYTHONPATH}"

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

EXIT_CODE=0

if [[ $# -eq 0 ]] ; then
    for TEST_ENV in $(find ${TEST_ENV_FOLDER} -name "*.test.env");
    do
        echo "Running tests for env ${TEST_ENV}."
        source ${TEST_ENV}
        run_tests ${TEST_ENV}
    done

    # Generate merged report
    cd ${log_dir} ; rebot $(find . -name "output.xml") ; cd ..
else
    if [[ $1 == *.test.env ]]
    then
        echo "Running test env: $1"
        source $1
        run_tests $1
    else
        echo "Running robot with arguments: \"$@\""
        robot  --outputdir ${log_dir} "$@"
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

exit ${EXIT_CODE}
