cmake_minimum_required(VERSION 3.5)

project(hello-world LANGUAGES C)

add_executable(hello-world hello-world.c)

install(TARGETS hello-world)

install(FILES hello-world.crinit DESTINATION /etc/crinit/crinit.d/)

SET (CPACK_SET_DESTDIR "/usr/local/bin/")
