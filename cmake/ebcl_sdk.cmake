macro(validate_arg_mod VAL_NAME VAL_MOD)
    list(LENGTH arg_${VAL_NAME} ${VAL_NAME}_len)
    math(EXPR ${VAL_NAME}_len_ok "${${VAL_NAME}_len} % ${VAL_MOD}")

    if(NOT (${VAL_NAME}_len_ok EQUAL 0))
        message(FATAL_ERROR "${CMAKE_CURRENT_FUNCTION}: Invalid number of arguments to ${VAL_NAME}")
    endif()
endmacro()

macro(validate_arg_opt VAL_NAME VAL_SIZE)
    list(LENGTH arg_${VAL_NAME} ${VAL_NAME}_len)
    if(NOT (${VAL_NAME}_len EQUAL ${VAL_SIZE}))
        message(FATAL_ERROR "${CMAKE_CURRENT_FUNCTION}: ${VAL_NAME} must have exactly ${VAL_SIZE} arguments or be omitted")
    endif()
endmacro()

macro(convert_template)
    if(config MATCHES "\.in$")
        block(PROPAGATE dependent_targets dependent_files config)
            while(arg_ARTIFACT)
                list(POP_FRONT arg_ARTIFACT target varname)
                list(APPEND dependent_targets ${target})
                get_target_property(${varname} ${target} ARTIFACT)
                list(APPEND dependent_files ${${varname}})
            endwhile()
            while(arg_OUTPUT_DIR)
                list(POP_FRONT arg_OUTPUT_DIR target varname)
                list(APPEND dependent_targets ${target})
                get_target_property(${varname} ${target} OUTPUT_DIR)
                file(GLOB_RECURSE all_files LIST_DIRECTORIES false ${${varname}}/*)
                list(APPEND dependent_files ${all_files})
            endwhile()
            cmake_path(GET config PARENT_PATH OWN_DIR)
            set(config_in "${config}")
            string(REGEX REPLACE "\.in$" "" config "${config_in}")
            cmake_path(GET config FILENAME config)
            string(PREPEND config "${build_dir}/")
            configure_file(
                ${config_in}
                ${config}
                @ONLY
            )
        endblock()
    endif()
endmacro()


function(add_rootfs target config)
    set(options "")
    set(oneValueArgs "")
    set(multiValueArgs ARTIFACT OUTPUT_DIR)
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )

    validate_arg_mod(ARTIFACT 2)
    validate_arg_mod(OUTPUT_DIR 2)

    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(REAL_PATH ${config} config BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    file(MAKE_DIRECTORY ${build_dir})

    convert_template()

    add_custom_command(
        OUTPUT ${build_dir}/root.tar
        COMMAND sh -c "root_generator --no-config ${config} ${build_dir} >${build_dir}/root.tar.log 2>&1"
        DEPENDS ${config} ${dependent_files}
        BYPRODUCTS ${build_dir}/root.tar.log
        VERBATIM
    )

    add_custom_command(
        OUTPUT ${build_dir}/root.config.tar
        COMMAND sh -c "root_configurator ${config} ${build_dir}/root.tar ${build_dir}/root.config.tar >${build_dir}/root.tar.config.log 2>&1"
        DEPENDS ${config} ${dependent_files}
                ${build_dir}/root.tar
        BYPRODUCTS ${build_dir}/root.tar.config.log
        VERBATIM
    )

    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/root.config.tar
    )
    if(DEFINED dependent_targets)
        add_dependencies(${target} ${dependent_targets})
    endif()

    set_property(
        TARGET ${target}
        PROPERTY ARTIFACT ${build_dir}/root.config.tar
    )
endfunction()


function(add_initrd target config)
    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(REAL_PATH ${config} config BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    file(MAKE_DIRECTORY ${build_dir})

    add_custom_command(
        OUTPUT ${build_dir}/initrd.img
        COMMAND sh -c "initrd_generator ${config} ${build_dir} >${build_dir}/initrd.img.log 2>&1"
        DEPENDS ${config}
        BYPRODUCTS ${build_dir}/initrd.img.log
        VERBATIM
    )

    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/initrd.img
    )

    set_property(
        TARGET ${target}
        PROPERTY ARTIFACT ${build_dir}/initrd.img
    )
endfunction()


function(add_kernel target config)
    set(options UNPACK)
    set(oneValueArgs "")
    set(multiValueArgs "")
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )
    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(REAL_PATH ${config} config BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    file(MAKE_DIRECTORY ${build_dir})

    if(arg_UNPACK)
        set(target_filename Image)
        set(target_command
            sh -c "( zcat ${build_dir}/vmlinuz* > ${build_dir}/Image || mv ${build_dir}/vmlinux* ${build_dir}/${target_filename} ) >/dev/null 2>&1"
        )
    else()
        set(target_filename vmlinuz)
        set(target_command
            sh -c "mv ${build_dir}/vmlinuz* ${build_dir}/${target_filename}"
        )
    endif()

    add_custom_command(
        OUTPUT ${build_dir}/${target_filename}
        COMMAND sh -c "boot_generator ${config} ${build_dir} >${build_dir}/Image.log 2>&1"
        COMMAND ${target_command}
        DEPENDS ${config}
        BYPRODUCTS ${build_dir}/Image.log
        VERBATIM
    )

    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/${target_filename}
    )

    set_property(
        TARGET ${target}
        PROPERTY ARTIFACT ${build_dir}/${target_filename}
    )
endfunction()


function(add_image target config)
    set(options "")
    set(oneValueArgs "")
    set(multiValueArgs ARTIFACT)
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )

    validate_arg_mod(ARTIFACT 2)

    set(dependent_targets)
    set(dependent_files)
    block(PROPAGATE dependent_targets dependent_files)
        while(arg_ARTIFACT)
            list(POP_FRONT arg_ARTIFACT target varname)
            list(APPEND dependent_targets ${target})
            get_target_property(${varname} ${target} ARTIFACT)
            list(APPEND dependent_files ${${varname}})
        endwhile()
        configure_file(
            ${config}
            image.yaml
            @ONLY
        )
    endblock()

    add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/image.raw
        COMMAND sh -c "embdgen -o ${CMAKE_CURRENT_BINARY_DIR}/image.raw ${CMAKE_CURRENT_BINARY_DIR}/image.yaml >${CMAKE_CURRENT_BINARY_DIR}/image.raw.log 2>&1"
        DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/image.yaml ${dependent_files}
        BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/image.raw.log
        VERBATIM
    )
    add_custom_target(
        ${target} ALL
        DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/image.raw
    )
    add_dependencies(${target} ${dependent_targets})
    set_target_properties(
        ${target}
        PROPERTIES ARTIFACT ${CMAKE_CURRENT_BINARY_DIR}/image.raw
    )
endfunction()


function(add_run_qemu target)
    set(options "")
    set(oneValueArgs ARCH KERNEL IMAGE MEMORY CPUS MACHINE INITRD NET_CONFIG CMDLINE)
    set(multiValueArgs TCP_FORWARD)
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )

    if(NOT DEFINED arg_ARCH)
        set(arg_ARCH aarch64)
    endif()

    if(NOT TARGET ${arg_KERNEL})
        message(FATAL_ERROR "add_run_qemu: Parameter KERNEL is not a target")
    endif()

    if(NOT TARGET ${arg_IMAGE})
        message(FATAL_ERROR "add_run_qemu: Parameter IMAGE is not a target")
    endif()

    if((DEFINED arg_INITRD) AND (NOT TARGET ${arg_INITRD}))
        message(FATAL_ERROR "add_run_qemu: Parameter INITRD is not a target")
    endif()

    validate_arg_mod(TCP_FORWARD 2)

    if(NOT DEFINED arg_MEMORY)
        set(arg_MEMORY 4096)
    endif()

    if(DEFINED arg_CPUS)
        set(cpus -smp ${arg_CPUS})
    endif()

    set(tcp_forward "")
    while(arg_TCP_FORWARD)
        list(POP_FRONT arg_TCP_FORWARD src dest)
        string(APPEND tcp_forward ",hostfwd=tcp:${src}-${dest}")
    endwhile()

    if(arg_ARCH STREQUAL "aarch64")
        set(machine -M virt,virtualization=true,gic-version=3 -cpu cortex-a57)
        set(net_device virtio-net-device)
        set(block_device virtio-blk-device)
    else()
        set(net_device virtio-net-pci)
        set(block_device virtio-blk)
    endif()

    if(DEFINED arg_INITRD)
        get_target_property(initrd ${arg_INITRD} ARTIFACT)
        list(PREPEND initrd -initrd)
    endif()

    if(DEFINED arg_NET_CONFIG)
        set(net_config ",${arg_NET_CONFIG}")
    endif()

    if(DEFINED arg_CMDLINE)
        set(cmdline -append ${arg_CMDLINE})
    endif()

    get_target_property(kernel ${arg_KERNEL} ARTIFACT)
    get_target_property(image ${arg_IMAGE} ARTIFACT)
    add_custom_target(
        ${target}
        COMMENT "Launching Qemu"
        COMMAND
            qemu-system-${arg_ARCH}
                ${machine}
                -m ${arg_MEMORY}
                ${cpus}
                -serial stdio
                -nographic
                -monitor none
                -kernel ${kernel}
                ${initrd}
                ${cmdline}
                -drive if=none,format=raw,file=${image},id=vd0
                -netdev user,id=net0${net_config}${tcp_forward}
                -device ${net_device},netdev=net0
                -device ${block_device},drive=vd0
        VERBATIM
    )
    add_dependencies(${target} ${arg_KERNEL} ${arg_IMAGE} ${arg_INITRD})
endfunction()


function(add_hypervisor_config target config)
    set(options "")
    set(oneValueArgs "")
    set(multiValueArgs SPECIALIZATION)
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )
    validate_arg_opt(SPECIALIZATION 2)

    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(MAKE_DIRECTORY ${build_dir})
    file(REAL_PATH ${config} config BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    set(specialization_args "")
    if(DEFINED arg_SPECIALIZATION)
        list(POP_FRONT arg_SPECIALIZATION repo spec_deb)
        file(REAL_PATH ${repo} repo BASE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
        set(specialization_args "--repo-config ${repo} --specialization-package ${spec_deb}")
    endif()

    add_custom_command(
        COMMENT "Generating hypervisor configuration"
        OUTPUT ${build_dir}/modules.list
        COMMAND sh -c "hypervisor_config ${specialization_args} ${config} ${build_dir} >${build_dir}.log 2>&1"
        BYPRODUCTS ${build_dir}.log
        DEPENDS ${config}
        VERBATIM
    )

    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/modules.list
    )

    set_target_properties(
        ${target}
        PROPERTIES OUTPUT_DIR ${build_dir}
    )
endfunction()


function(add_hypervisor target config)
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
    
    file(GLOB config_files ${config_dir}/*)
    add_custom_command(
        OUTPUT ${build_dir}/bootstrap.uimage
        COMMAND rm -rf ${build_dir}/config
        COMMAND sh -c "boot_generator ${config} ${build_dir} >${build_dir}/bootstrap.uimage.log 2>&1"
        COMMAND touch ${build_dir}/bootstrap.uimage
        DEPENDS ${config}
                ${dependent_files}
        BYPRODUCTS ${build_dir}/bootstrap.uimage.log
        VERBATIM
    )
    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/bootstrap.uimage
    )
    if(DEFINED dependent_targets)
        add_dependencies(${target} ${dependent_targets})
    endif()

    set_target_properties(
        ${target}
        PROPERTIES ARTIFACT ${build_dir}/bootstrap.uimage
    )
endfunction()


function(add_preprocess_devicetree target source)
    set(options "")
    set(oneValueArgs INCLUDE)
    set(multiValueArgs "")
    cmake_parse_arguments(PARSE_ARGV 0 arg
        "${options}" "${oneValueArgs}" "${multiValueArgs}"
    )

    set(build_dir ${CMAKE_CURRENT_BINARY_DIR}/${target}.target)
    file(MAKE_DIRECTORY ${build_dir})

    get_filename_component(source_name ${source} NAME)
    get_filename_component(source_dir ${source} DIRECTORY)

    list(TRANSFORM arg_INCLUDE PREPEND -I)
    add_custom_command(
        OUTPUT ${build_dir}/${source_name}
        COMMAND 
            cpp
                -nostdinc
                -undef
                -x assembler-with-cpp
                ${source}
                -I ${source_dir}
                ${arg_INCLUDE}
                -o ${build_dir}/${source_name}
                -MMD -MF ${build_dir}/${source_name}.d -MT ${build_dir}/${source_name}
        DEPFILE ${build_dir}/${source_name}.d
        VERBATIM
    )

    add_custom_target(
        ${target} ALL
        DEPENDS ${build_dir}/${source_name}
    )
    set_target_properties(
        ${target}
        PROPERTIES ARTIFACT ${build_dir}/${source_name}
    )
endfunction()
