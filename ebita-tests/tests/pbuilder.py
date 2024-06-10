from ebita.api.test_class_base import TestClassBase
from utils import run_container, run_command, stop_container

class Pbuilder(TestClassBase):
    def setup_class():
        """Run the Docker SDK container."""
        run_container()

    def teardown_class():
        """Stop the Docker SDK container."""
        stop_container()

    def package_config_files(self):
        # delete old metadata
        run_command('rm -rf /workspace/apps/my-config/debian')
        # generate debian metadata
        run_command('prepare_deb_all_metadata my-config')
        (lines, _stdout, _stderr) = run_command('file /workspace/apps/my-config/debian/')
        assert lines[-2] == '/workspace/apps/my-config/debian/: directory'
        # ensure it's an all package
        (_lines, stdout, _stderr) = run_command('cat /workspace/apps/my-config/debian/control')
        assert 'Architecture: all' in stdout
        # generate the install file
        run_command('make_deb_install /workspace/apps/my-config')
        # install file exists
        (lines, _stdout, _stderr) = run_command('file /workspace/apps/my-config/debian/install')
        assert lines[-2] == '/workspace/apps/my-config/debian/install: ASCII text'
        # check file content
        (lines, _stdout, _stderr) = run_command('cat /workspace/apps/my-config/debian/install')
        assert lines[-2] == './etc/ssh/sshd_config.d/10-root-login.conf /etc/ssh/sshd_config.d'
        # build Debian package - arch is mandatory parameter
        (lines, _stdout, _stderr) = run_command('build_package my-config amd64')
