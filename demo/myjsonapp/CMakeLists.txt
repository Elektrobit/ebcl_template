cmake_minimum_required(VERSION 3.10)

project(MyJsonApp)

set(CMAKE_CXX_STANDARD 11)

find_package(PkgConfig REQUIRED)
pkg_check_modules(JSONCPP jsoncpp)

include_directories(${JSONCPP_INCLUDE_DIRS})

add_executable(myjsonapp main.cpp)

target_link_libraries(myjsonapp ${JSONCPP_LIBRARIES})

install(TARGETS myjsonapp DESTINATION)

SET (CPACK_SET_DESTDIR "/usr/local/bin/")
