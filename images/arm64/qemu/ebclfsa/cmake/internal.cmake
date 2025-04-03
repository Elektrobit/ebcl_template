function(add_cmake_build target source preset)
    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(REAL_PATH ${source} source BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    add_custom_target(
        ${target} ALL
        COMMAND
            mkdir -p ${build_dir}
        COMMAND
            sh -c "cmake -S ${source} -B ${build_dir} --preset ${preset} >${build_dir}/cmake.log 2>&1"
        COMMAND
            sh -c "cmake --build ${build_dir} >>${build_dir}/cmake.log 2>&1"
        COMMAND
            sh -c "cmake --install ${build_dir} --prefix ${build_dir}/install >>${build_dir}/cmake.log 2>&1"
        BYPRODUCTS ${build_dir}
        VERBATIM
    )

    set_target_properties(
        ${target}
        PROPERTIES OUTPUT_DIR ${build_dir}/install
    )
endfunction()


function(add_uboot target config)
    set(options "")
    set(oneValueArgs "")
    set(multiValueArgs ARTIFACT OUTPUT_DIR)
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )

    validate_arg_mod(ARTIFACT 2)
    validate_arg_mod(OUTPUT_DIR 2)

    file(REAL_PATH ${config} config BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(MAKE_DIRECTORY ${build_dir})

    convert_template()

    add_custom_command(
        OUTPUT ${build_dir}/uboot-qemu-bart.elf
        COMMAND sh -c "boot_generator ${config} ${build_dir} >${build_dir}/uboot-qemu-bart.elf.log 2>&1"
        DEPENDS ${config} ${dependent_files}
        BYPRODUCTS ${build_dir}/uboot-qemu-bart.elf.log
        VERBATIM
    )

    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/uboot-qemu-bart.elf
    )
    if(DEFINED dependent_targets)
        add_dependencies(${target} ${dependent_targets})
    endif()

    set_property(
        TARGET ${target}
        PROPERTY ARTIFACT ${build_dir}/uboot-qemu-bart.elf
    )
endfunction()
