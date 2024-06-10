from ebita.api.test_class_base import TestClassBase
from utils import run_container, run_command, stop_container

class Kiwi(TestClassBase):
    def setup_class():
        """Run the Docker SDK container."""
        run_container()

    def teardown_class():
        """Stop the Docker SDK container."""
        stop_container()

    def kiwi_is_available(self):
        (lines, _stdout, _stderr) = run_command('source /build/venv/bin/activate; kiwi-ng -v')
        assert lines[-2].startswith('KIWI ')
