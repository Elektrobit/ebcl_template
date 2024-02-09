#!/bin/bash 

set -eu

DEMO_APP_ARGUMENT_SHORT="-da"
DEMO_APP_ARGUMENT="--demo-app"
DEMO_APP_INFO="demo app name (myjsonapp|hello-world)"
DEMO_APP_SELECTION=""

APP_START_ARGUMENT_SHORT="-as"
APP_START_ARGUMENT="--app-start"
APP_START_INFO="type of application start (manual|crinit|systemd)"
APP_START_SELECTION=""

usage()
{
    echo -e "This script is used to copy files of a selected demo application to the app folder used for building the application."
    echo ""
    echo -e "\e[7mUsage :\e[0m"
    echo ""
    echo -e "copy_demo_app.sh ${DEMO_APP_ARGUMENT_SHORT}|${DEMO_APP_ARGUMENT} <${DEMO_APP_INFO}>"
    echo -e "                 ${APP_START_ARGUMENT_SHORT}|${APP_START_ARGUMENT} <${APP_START_INFO}>"
    echo ""
    echo -e "${DEMO_APP_ARGUMENT_SHORT} | ${DEMO_APP_ARGUMENT}   : ${DEMO_APP_INFO} (Required)"
    echo -e "${APP_START_ARGUMENT_SHORT} | ${APP_START_ARGUMENT}  : ${APP_START_INFO} (Required)"
    echo -e "-h  | --help       : Display this usage message"
}


PARAMETER_LIST=$*
if [ $# -lt 1 ] ; then
    echo -e "\e[91m[ERROR]\e[0m Missing required argument!"
    usage
    exit 1
fi

while [ $# -gt 0 ] ; do
    case $1 in
    "${DEMO_APP_ARGUMENT}" | "${DEMO_APP_ARGUMENT_SHORT}")
        if [ $# -lt 2 ] ; then
            echo -e "\e[91m[ERROR]\e[0m Missing required argument!"
            usage
            exit 1
        fi
        DEMO_APP_SELECTION="${2}"
        shift
        ;;
    "${APP_START_ARGUMENT}" | "${APP_START_ARGUMENT_SHORT}")
        if [ $# -lt 2 ] ; then
            echo -e "\e[91m[ERROR]\e[0m Missing required argument!"
            usage
            exit 1
        fi
        APP_START_SELECTION="${2}"
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        echo -e "\e[91m[ERROR]\e[0m Unknown argument '$1' not found !"
        usage
        exit 1
    esac
    shift
done


DEMO_FOLDER="/build/workspace/demo"
BUILD_APP_FOLDER="/build/app"

if [[ -z ${DEMO_APP_SELECTION} ]] ; then
    echo -e "\e[91m[ERROR]\e[0m Missing required argument!"
    usage
    exit 1
fi

if [[ -z ${APP_START_SELECTION} ]] ; then
    echo -e "\e[91m[ERROR]\e[0m Missing required argument!"
    usage
    exit 1
fi

case ${DEMO_APP_SELECTION} in
"myjsonapp" | "hello-world")
    DEMO_APP_FOLDER="${DEMO_FOLDER}/${DEMO_APP_SELECTION}"
    if [[ ! -d "${DEMO_APP_FOLDER}" ]] ; then
        echo -e "\e[91m[ERROR]\e[0m Not existing folder '${DEMO_APP_FOLDER}' of demo application '${DEMO_APP_SELECTION}'!"
        exit 1
    fi
    ;;
*)
    echo -e "\e[91m[ERROR]\e[0m Not supported demo application '${DEMO_APP_SELECTION}'!"
    usage
    exit 1
esac

case ${APP_START_SELECTION} in
"manual" | "crinit" | "systemd")
    ;;
*)
    echo -e "\e[91m[ERROR]\e[0m Not supported application start type '${APP_START_SELECTION}'!"
    usage
    exit 1
esac

rm -rf ${BUILD_APP_FOLDER}/*
cp ${DEMO_APP_FOLDER}/CMakeLists.txt ${BUILD_APP_FOLDER}/
for FILE in $(find ${DEMO_APP_FOLDER} -name "*.c") ; do
    cp ${FILE} ${BUILD_APP_FOLDER}/
done
for FILE in $(find ${DEMO_APP_FOLDER} -name "*.cpp") ; do
    cp ${FILE} ${BUILD_APP_FOLDER}/
done

case ${APP_START_SELECTION} in
"crinit")
    cp ${DEMO_APP_FOLDER}/*.crinit ${BUILD_APP_FOLDER}/
    sed -i "s/SET (CPACK_SET_DESTDIR \"\/usr\/local\/bin\/\")/install(FILES ${DEMO_APP_SELECTION}.crinit DESTINATION \/etc\/crinit\/crinit.d\/)\n\nSET (CPACK_SET_DESTDIR \"\/usr\/local\/bin\/\")/g" ${BUILD_APP_FOLDER}/CMakeLists.txt
    ;;
"systemd")
    cp ${DEMO_APP_FOLDER}/*.service ${BUILD_APP_FOLDER}/
    sed -i "s/SET (CPACK_SET_DESTDIR \"\/usr\/local\/bin\/\")/install(FILES ${DEMO_APP_SELECTION}.service DESTINATION \/lib\/systemd\/system\/)\n\nSET (CPACK_SET_DESTDIR \"\/usr\/local\/bin\/\")/g" ${BUILD_APP_FOLDER}/CMakeLists.txt
    ;;
esac

