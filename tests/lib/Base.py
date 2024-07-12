from utils import run_command

class Base:
        
    def sdk_version(self, version: str):
        (lines, _stdout, _stderr) = run_command('cat /etc/sdk_version')
        print(lines)
        assert lines[-2] == version
        
    def ensure_ebcl_user_is_used(self):
        (_lines, stdout, _stderr) = run_command('id')
        assert 'uid=1000(ebcl)' in stdout
        assert 'gid=1000(ebcl)' in stdout
        
    def ensure_environment_is_ok(self):
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
