add_executable(li_demo li_main.c)

target_include_directories(li_demo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../common)
target_link_libraries(li_demo shmlib)

install(TARGETS li_demo DESTINATION ${CMAKE_INSTALL_BINDIR})
