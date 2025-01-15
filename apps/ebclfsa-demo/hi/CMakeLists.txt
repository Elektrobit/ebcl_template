
# High integrity applications must be modified, for the linux kernel
# to recognize them as high integrity applications.
function(target_enable_hi target)
  add_custom_command(
    TARGET ${target}
    POST_BUILD
    COMMAND lisa-elf-enabler $<TARGET_FILE:${target}>
  )
endfunction()

add_executable(hi_main hi_main.c)

target_include_directories(hi_main PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../common)
target_link_libraries(hi_main shmlib)
target_enable_hi(hi_main)


add_executable(hi_forward hi_forward.c)

target_include_directories(hi_forward PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../common)
target_link_libraries(hi_forward shmlib)
target_enable_hi(hi_forward)


install(TARGETS hi_main hi_forward DESTINATION /)
