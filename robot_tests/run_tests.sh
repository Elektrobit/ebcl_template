#!/bin/bash

if [ -n "$FORCE_CLEAN_REBUILD" ]; then
    echo "Enforcing image rebuild..."
    export SDK_ROBOT_SKIP_CLEAN="0"
else
    echo "Enforced image rebuild is off..."
fi

test_lib_folder=$(realpath ./lib)

export PYTHONPATH="${test_lib_folder}:${PYTHONPATH}"

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
    robot --outputdir ${log_dir} *.robot
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

ln -s ${log_dir}/report.html .
ln -s ${log_dir}/log.html .
ln -s ${log_dir}/output.xml .
