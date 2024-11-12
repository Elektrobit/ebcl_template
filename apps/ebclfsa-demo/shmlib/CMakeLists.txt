add_library(shmlib
  src/shmlib_shm.c
  src/shmlib_lock.c
  src/shmlib_logger.c
  src/shmlib_hi_app.c
  src/shmlib_proxyshm.c
  src/shmlib_ringbuffer.c
  src/shmlib_watchdog.c
)

if(BUILD_HI)
  target_sources(shmlib PRIVATE src/shmlib_hi_shm.c)
  target_compile_definitions(shmlib PRIVATE BUILD_HI)
else()
  target_sources(shmlib PRIVATE src/shmlib_li_shm.c)
endif()

target_include_directories(shmlib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
