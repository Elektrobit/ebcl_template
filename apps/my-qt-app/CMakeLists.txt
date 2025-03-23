cmake_minimum_required(VERSION 3.12)

project(MyQTApp VERSION 1.0.0 LANGUAGES CXX)

# Qt 6 requires a compiler supporting C++ version 17 or newer.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include GNUInstallDirs to determine the correct values for CMAKE_INSTALL_*
include(GNUInstallDirs)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

# automatically create rules to invoke Qt's User Interface Compiler (uic) on .ui source files.
# uncomment if we have *.ui
# qt_standard_project_setup()

add_executable(${PROJECT_NAME}
    helloworld.cpp
)

# link against Qt6::Widgets instead of Qt6::Core.
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Widgets)


set_target_properties(${PROJECT_NAME} PROPERTIES
    # Enable Qt't Meta-Object Compiler to handle the Qt moc preprocessor automatically
    AUTOMOC ON
)

# Installation configuration
install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_BINDIR})