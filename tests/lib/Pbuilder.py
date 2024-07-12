from utils import run_command

class Pbuilder:
        
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
        # delete old results
        run_command('rm -rf /workspace/results/packages/my-config_*')
        # build Debian package - arch is mandatory parameter
        (lines, _stdout, _stderr) = run_command('build_package my-config')
        # find result folder
        (lines, _stdout, _stderr) = run_command('find /workspace/results/packages -type \"d\" -name \"my-config_*\"')
        result_folder = lines[-2]
        # check deb exists
        (lines, _stdout, _stderr) = run_command(f'file {result_folder}/my-config_0.0.1_all.deb')
        print(f'Line: {lines[-2]}')
        assert lines[-2].startswith(f'{result_folder}/my-config_0.0.1_all.deb: Debian binary package (format 2.0)')
        # check deb content
        (lines, _stdout, _stderr) = run_command(f'cd {result_folder}; ar x my-config_0.0.1_all.deb; tar xf data.tar.zst; file etc/ssh/sshd_config.d/10-root-login.conf')
        assert lines[-2] == ('etc/ssh/sshd_config.d/10-root-login.conf: ASCII text')
    
    def package_app(self, arch: str):
        #================================
        # Prepare Debian metadata for app
        #================================
        # delete old metadata
        run_command('rm -rf /workspace/apps/my-json-app/debian')
        # generate debian metadata
        run_command('prepare_deb_metadata my-json-app')
        (lines, _stdout, _stderr) = run_command('file /workspace/apps/my-json-app/debian/')
        assert lines[-2] == '/workspace/apps/my-json-app/debian/: directory'
        # ensure it's an all package
        (_lines, stdout, _stderr) = run_command('cat /workspace/apps/my-json-app/debian/control')
        assert 'Architecture: any' in stdout
        # add app build time dependencies        
        run_command('sed -i \'5s@.*@Build-Depends: debhelper-compat (= 13), cmake, pkg-config, libjsoncpp-dev@g\' /workspace/apps/my-json-app/debian/control')
        
        #==============
        # Build the app
        #==============
        # delete old results
        run_command('rm -rf /workspace/results/packages/my-json-app_*')
        # build Debian packages
        print(f'Building package for arch {arch}.')
        run_command(f'build_package my-json-app {arch}')
        # find result folder
        (lines, _stdout, _stderr) = run_command('find /workspace/results/packages -type \"d\" -name \"my-json-app_*\"')
        result_folder = lines[-2]
        print(f'Result folder: {result_folder}')
        # check deb exists
        (lines, _stdout, _stderr) = run_command(f'file {result_folder}/my-json-app_0.0.1_{arch}.deb')
        print(f'Line: {lines[-2]}')
        assert lines[-2].startswith(f'{result_folder}/my-json-app_0.0.1_{arch}.deb: Debian binary package (format 2.0)')

