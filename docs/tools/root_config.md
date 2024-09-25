# Root configurator

A root tarball can be configured with user scripts by the root generator.

**root_configurator** — Built a root tarball

## Description

Configures a tarball with user privided scripts.
Splitting the root tarball generation from the configuration allows for fast configuration adaptions.
The synopsis is `root_configurator <root>.yaml <input>.tar <output>.tar`

![BuildTools](../assets/root_config.drawio.png)

The internal steps are:

 1. Read in YAML configuration file
 2. If sysroot is configured add generic sysroot packages like g++
 3. Depending on the configuration build the image with kiwi or elbe
 4. If configuration is not skipped run config.sh script if present
 5. Copy image tar to output folder

## Configuration

```yaml
# You can define multiple configuration scripts that will run "in" the tarball
scripts:
  - name: <name.sh>
    env: <chroot|chfake>
  - name: ...
```
