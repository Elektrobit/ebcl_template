from ebita.api.test_class_base import TestClassBase
from utils import run_container, run_command, stop_container

class Appdev(TestClassBase):
    def setup_class():
        """Run the Docker SDK container."""
        run_container()

    def teardown_class():
        """Stop the Docker SDK container."""
        stop_container()

    def cmake_app_x86_64(self):
        # prepare sysroot
        # asumption: /build/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.tar.xz is available
        run_command('rm -rf /workspace/sysroot_x86_64/*', check=False, no_error=False)
        run_command('cp /build/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.tar.xz /workspace/sysroot_x86_64/')
        run_command('cd /workspace/sysroot_x86_64/; tar xf qemu_crinit_x86_64.*.tar.xz')
        # delete old result
        run_command('rm -rf /build/results/apps/my-json-app_x86_64*')
        # build image
        run_command('cmake_x86_64 my-json-app')
        (lines, _stdout, _stderr) = run_command('file /build/results/apps/my-json-app_x86_64_*/MyJsonApp')
        assert 'ELF 64-bit LSB pie executable, x86-64' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/apps/my-json-app_x86_64_*/MyJsonApp')
        assert 'ELF 64-bit LSB pie executable, x86-64' in lines[-2]

    def cmake_app_aarch64(self):
        # prepare sysroot
        # asumption: /build/results/images/qemu_crinit_aarch64/qemu_crinit_aarch64.*.tar.xz is available
        run_command('rm -rf /workspace/sysroot_aarch64/*', check=False, no_error=False)
        run_command('cp /build/results/images/qemu_crinit_aarch64/qemu_crinit_aarch64.*.tar.xz /workspace/sysroot_aarch64/')
        run_command('cd /workspace/sysroot_aarch64/; tar xf qemu_crinit_aarch64.*.tar.xz')
        # delete old result
        run_command('rm -rf /build/results/apps/my-json-app_aarch64*')
        # build image
        run_command('cmake_aarch64 my-json-app')
        (lines, _stdout, _stderr) = run_command('file /build/results/apps/my-json-app_aarch64_*/MyJsonApp')
        assert 'ELF 64-bit LSB pie executable, ARM aarch64' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/apps/my-json-app_aarch64_*/MyJsonApp')
        assert 'ELF 64-bit LSB pie executable, ARM aarch64' in lines[-2]
