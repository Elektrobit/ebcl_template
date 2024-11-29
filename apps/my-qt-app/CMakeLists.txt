cmake_minimum_required(VERSION 3.12)

project(MyQTApp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include GNUInstallDirs to determine the correct values for CMAKE_INSTALL_*
include(GNUInstallDirs)

find_package(Qt6 REQUIRED COMPONENTS Widgets)

add_executable(${PROJECT_NAME}
    helloworld.cpp
)

target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Widgets)

set_target_properties(${PROJECT_NAME} PROPERTIES
    # Enable Qt't Meta-Object Compiler
    AUTOMOC ON
)

#set(Qt6_NO_WRAP_VULKAN_HPP ON)
#set(Qt6_NO_XKB ON)

# Installation configuration
install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_BINDIR})
