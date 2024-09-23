# Packaging applications for EB corbos Linux

EB corbos Linux makes use of Debian packages, which are described in full detail in the [Debian Policy Manual](https://www.debian.org/doc/debian-policy/ch-archive.html). On a high level, there are two types of packages, source packages and binary packages.

The source packages consist of a _dsc_ file containing the metadata of the package and typically referencing source tarballs belonging to this package.
As an example, you can take a look at the [_dsc_ of the _nano_ editor](http://archive.ubuntu.com/ubuntu/pool/main/n/nano/nano_8.1-1.dsc). The source tarball contains a _debian_ subfolder, and this subfolder contains all metadata of this package, and the binary packages which can be built using this source package, including the build instructions.
Debian tooling like [pbuilder](https://wiki.ubuntu.com/PbuilderHowto) can be used to build the binary packages out of a source package, for all supported platforms and variants.


The binary packages are Unix AR archives containing a file _debian-binary_, giving the version number of the used Debian binary package format, a _control.tar.gz_, containing the metadata of the package, a _data.tar.gz_, which is extracted to the filesystem when the package is installed, and potentially further metadata files.
The advantage of using Debian binary packages and apt repositories is that you have a signature chain from your copy of the public key of the apt repository to the Debian binary package you download, which ensures that the package was provided by the right vendor, and was not manipulated on the way.
Bundling the metadata with the software allows apt to ensure that the package is compatible with the target environment, and that all dependencies are fulfilled.
For all installed packages, the package information is installed into _/usr/share/doc_. You can consult this folder to get the changelog and license information for your installed packages.

If you develop applications for EB corbos Linux, which shall be installed in the root filesystem, especially during build time, we recommend to package these applications, since this ensures that the right version is installed, all dependencies are available, and allows an easy reuse.
If you develop applications which shall not be part of the root filesystem, e.g.
to update them separately from the root image, a bundling according to the needs of the update solution is necessary, and a Debian packaging is not required.

We don’t recommend apt as an update tool for embedded solutions, since it doesn’t support an A/B update schema, and it’s not prepared to be used together with a read-only and dm-verity protected root filesystem, which you may use if you implement a secure boot solution.
For such scenarios, the existing embedded update solutions, and containers are much better solutions.
If you need a customized update solution, or consulting for building online updateable HPC platforms, please [contact us](https://www.elektrobit.com/contact-us/).

## Preparing the Debian package metadata

The first step to create a Debian package is to add the required metadata.
You don’t need to do this by hand, there are various tools which will generate template metadata.
We recommend _dh_make_ to generate the metadata.
If you want to explore other tooling for creating packages from a source, refer to https://wiki.debian.org/Packaging/SourcePackage.


The  _dh_make_ tool has some expectations about the folder name, and as a comfort feature the EBcL SDK provides a helper script _prepare_deb_metadata_ to generate the metadata for an app.
To generate the Debian metadata for an app contained in the _apps_ folder fo the workspace, you can run `prepare_deb_metadata [name of the app]`, e.g.
`prepare_deb_metadata my-json-app`. For the example applications, you can also make use of the corresponding build task _EBcL: Generate Debian metadata for app_, which shows up in the build tasks menu (_Ctrl + Shift + B_). This will add a new subfolder _debian_ to the app folder.


The generated metadata is just a template, and needs to be adjusted for successful building a package.
Open the new _debian/control_ and complete it.
At minimum, you need to change the value of  _Section_ to _misc_ or another valid value, and fill out the _Description_. If your app has build-time dependencies, you also need to add it to the _Build-Depends_ list.
For the _my-json-app_, the dependencies are:

```
Build-Depends: debhelper-compat (= 13), cmake, pkg-config, libjsoncpp-dev
```

Debian packages use several different metadata files.
The most important ones are:

- _control_: This file contains the details of the source and binary packages.
For more details, refer to https://www.debian.org/doc/debian-policy/ch-controlfields.html.

- _rules_: This file contains the package build rules that will be used to create the package.
This file is a kind of Makefile.
For more details, refer to https://www.debian.org/doc/debian-policy/ch-source.html#main-building-script-debian-rules.

- _copyright_: This file contains the copyright of the package in a machine-readable format.
For more details, refer to https://www.debian.org/doc/debian-policy/ch-archive.chtml#copyright-considerations.

- _changelog_: The changelog of the package itself.
It contains version number, revision, distribution, and urgency of the package.
For more details, refer to https://www.debian.org/doc/debian-policy/ch-source.html#debian-changelog-debian-changelog.

- _patches_: This folder can contain patches that are applied on top of the original source.
For more details, refer to https://www.debian.org/doc/debian-policy/ch-source.html#vendor-specific-patch-series.

## Packaging the application

If the package metadata is prepared, you can build the Debian packages for amd64 using [pbuilder](https://wiki.ubuntu.com/PbuilderHowto). The EBcL SDK provides also for _pbuilder_ a comfort script to build application packages.
You can run `build_package [name of the app] [architecture]`, e.g.
`prepare_deb_metadata my-json-app amd64`, to build the Debian binary package for your application.
The results will be written to _results/packages_.  For packaging the example applications, you can also make use of the corresponding build tasks _EBcL: Package app_, which shows up in the build tasks menu (_Ctrl + Shift + B_).

## Adding the package to an image

To make the new Debian package available for image builds, we need to provide it as part of an apt repository.
An apt repository can simply be a folder or a static server directory on the web, containing a `Release` and a `Packages.gz` file describing the contained packages.
When we have an apt repository containing our new package, we can add this repository to your image specification, and then add the package to the list of installed packages.

As mentioned before, apt repositories are signed, so we need a GPG key to sign the metadata of the local apt repository, which we will set up to provide our locally built packages.
There is again a comfort script and a VS Code build task to generate the key, but before generating the key, you should update the identity information contained in _identity/env_. When you have put your contact data in, you can generate the GPG key by running the task _EBcL: Generate signing key_, or running `gen_sign_key` in a shell.
To use an existing key, you can copy the keyring into the workspace folder _gpg-keys/.gnupg_.

When the key is available, you can generate the apt repository metadata by running the VS Code build task _EBcL: Prepare local repository_, or the command `prepare_repo_config`. The command adds the needed index files and signatures to the folder_results/packages_. Please be aware that all found packages are added to the apt index, and if you have multiple builds of the same package in the folder, it’s somehow random which package is picked.
It’s best to delete the old build, and re-run `prepare_repo_config` to ensure the expected package will be used.

To be able to use the repository in an image build, you need to serve it.
You can do this by running the VS Code task _EBcL: Serve local repository_ or the command `serve_packages`. Then you can add the apt repository to your image configuration using the IP address of the container, which get with `ip addr`:

```yaml
apt_repos:
  - apt_repo: http://<Container IP>
    distro: local
    components:
      - main
```
