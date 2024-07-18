set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc-11)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++-11)

set(CMAKE_FIND_ROOT_PATH  "/build/sysroot_aarch64")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(CMAKE_C_FLAGS "--sysroot /build/sysroot_aarch64/")
set(CMAKE_CXX_FLAGS "--sysroot /build/sysroot_aarch64/")

set(ENV{PKG_CONFIG_DIR} "")
set(ENV{PKG_CONFIG_LIBDIR} "${CMAKE_FIND_ROOT_PATH}/usr/lib/aarch64-linux-gnu/pkgconfig/:${CMAKE_FIND_ROOT_PATH}/usr/share/pkgconfig")
set(ENV{PKG_CONFIG_SYSROOT_DIR} ${CMAKE_FIND_ROOT_PATH})
