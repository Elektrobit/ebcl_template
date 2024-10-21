# Minimum CMake version required
cmake_minimum_required(VERSION 3.10)

# Project name
project(MeminfoReader)

# Set the C standard to C99 (you can change this to C11 or another version if needed)
set(CMAKE_C_STANDARD 99)

# Include GNUInstallDirs to determine the correct values for CMAKE_INSTALL_*
include(GNUInstallDirs)

# Add the executable target
add_executable(meminfo-reader meminfo_reader.c)

# Link the necessary libraries (in this case, we're linking the syslog library)
target_link_libraries(meminfo-reader PRIVATE ${CMAKE_REQUIRED_LIBRARIES})

# Installation configuration
install(TARGETS meminfo-reader DESTINATION ${CMAKE_INSTALL_BINDIR})