from utils import run_command

class Rust:
        
    def rustc_is_available(self):
        (lines, _stdout, _stderr) = run_command('rustc -V')
        assert lines[-2].startswith('rustc ')

    def cargo_is_available(self):
        (lines, _stdout, _stderr) = run_command('cargo -V')
        assert lines[-2].startswith('cargo ')
