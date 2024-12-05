# Building old Berrymill images

The previous versions up unto 1.2 of the EBcL SDK used _kiwi-ng_ for building images.
Using _kiwi-ng_ was a quite pragmatic choice, since it’s an established tool to build images from binary IT distribution packages. Nevertheless, it turned out that _kiwi-ng_ is not flexible enough to build typical embedded images.
Starting from EBcL SDK 1.3 the new _make_ and _generator_ based builds are used. In the EBcL SDK 2.0 furthermore _make_ was replaced with _task_. 
This approach has the advantage that it’s flexible enough for any imaginable build flow, and that the builds are much more efficient.
For EBcL 1.x, _kiwi-ng_ is still provided and supported, but support is dropped with the EBcL 2.x line and the old images are not supported anymore. Please migrate.
