cmake_minimum_required (VERSION 3.21 FATAL_ERROR)

project(
  ebclfsa-demo
  LANGUAGES C
)

include(GNUInstallDirs)

option(BUILD_HI "Build high integrity applications, otherwise build low integrity application" OFF)

add_compile_options(-Wall -Wextra -Werror)

add_subdirectory(shmlib)

if(BUILD_HI)
  add_subdirectory(hi)
else()
  add_subdirectory(li)
endif()

