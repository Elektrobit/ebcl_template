from ebita.api.test_class_base import TestClassBase
from utils import run_container, run_command, stop_container

class Rust(TestClassBase):
    def setup_class():
        """Run the Docker SDK container."""
        run_container()

    def teardown_class():
        """Stop the Docker SDK container."""
        stop_container()

    def rustc_is_available(self):
        (lines, _stdout, _stderr) = run_command('rustc -V')
        assert lines[-2].startswith('rustc ')

    def cargo_is_available(self):
        (lines, _stdout, _stderr) = run_command('cargo -V')
        assert lines[-2].startswith('cargo ')
