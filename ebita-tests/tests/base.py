from ebita.api.test_class_base import TestClassBase
from utils import run_container, run_command, stop_container

class Base(TestClassBase):

    def setup_class():
        """Run the Docker SDK container."""
        run_container()

    def teardown_class():
        """Stop the Docker SDK container."""
        stop_container()

    def sdk_version(self):
        """Check the SDK version"""
        (lines, _stdout, _stderr) = run_command('cat /etc/sdk_version')
        assert lines[-2] == '1.2'

    def user(self):
        """Check user"""
        (_lines, stdout, _stderr) = run_command('id')
        assert 'uid=1000(ebcl)' in stdout
        assert 'gid=1000(ebcl)' in stdout

    def environment(self):
        """Ensure environment is OK."""
        (lines, _stdout, _stderr) = run_command('env')
        for line in lines:
            if line.startswith('PATH'):
                assert '/build/bin' in line
            if line.startswith('PWD'):
                assert line == "PWD=/workspace"
            if line.startswith('DEBFULLNAME'):
                assert line == "DEBFULLNAME=Elektrobit Automotive GmbH"
            if line.startswith('DEBEMAIL'):
                assert line == "DEBEMAIL=info@elektrobit.com"
