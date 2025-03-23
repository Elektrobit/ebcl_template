```console
# tested with /workspace/images/arm64/beaglebone/beagleplay/systemd_weston
mkdir build
cd build
cmake --toolchain /build/cmake/toolchain-aarch64.cmake -B /workspace/apps/my-qt-app/build -S /workspace/apps/my-qt-app
make
```