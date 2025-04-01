# Performance tests

The EBcL test library provides a very simple setup for performance tests.
The idea of those performance tests are to implement a continuous monitoring, and detecting changes early.
It is not the idea to provide precise and stable performance measurements for the system under test.

The performance tests require special images,
which are configured to automatically shutdown when the startup is completed.
These images are assembled using a test overlay which is provided in a second partition,
and mounted in the early userspace,
if the kernel cmdline parameter _test_overlay_, pointing to the partition, is provided.
This is implemented for the _arm64/qemu/ebcl_ images.
You can find the implementation in the
[init.sh.template](https://github.com/Elektrobit/ebcl_template/images/arm64/qemu/ebcl/init.sh.template).

These test overlays provide a quite simple way to extend images with test extensions
in a very controlled manner, and make it easy to fully understand the impact of the
test extensions. They may be also helpful for other kind of tests which require modified images.

In general, we expect that also test extensions and manipulations are done during image build,
and not during test execution time. If a test requires image manipulations, a test specific
build target is created, which shall implement all changes in an easy to understand and
reproducible way.
This helps not only for the quality argumentation, but also helps in maintaining these modifications
when the images change over time, reduces the requirements for the test execution environment,
and allows to inspect the result of the manipulations.

The [performance tests implemented in qemu_performance.robot](https://github.com/Elektrobit/ebcl_template/robot_tests/qemu_performance.robot)
make use of the _Image_ class to build the test-specific images.
For a CI or hardware setup, this step needs to be separated,
but for the local QEMU build it helps to simplify the tests.

For executing the tests, the _Performance_ class is used.
This class runs the image, and expects that the image shuts down automatically.
During the run, the logs are collected by _ProcIO_ and extended with host timestamps.
After the run, the _Performance_ class collects the logs,
searches for given keywords as measurement points,
evaluates the times using the host timestamps,
and generates a test report.

This approach doesn't allow for highly precise and stable performance numbers,
since there is some variation and delay by reading the logs,
but it is simple and portable and should provide numbers in a precision of
a few 10 ms.
From our point of view, it's good enough to get a first idea of image changes,
and to setup some monitoring for performance degrades.

This test setup may change over time.
For more details, please consult the implementation.

