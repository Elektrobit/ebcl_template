from ebita.api.test_class_base import TestClassBase
from utils import run_container, run_command, stop_container

class Kiwi(TestClassBase):
    def setup_class():
        """Run the Docker SDK container."""
        run_container()

    def teardown_class():
        """Stop the Docker SDK container."""
        stop_container()

    def setup(self, image_name = None, image_appliance = None):
        self.image_name = image_name
        self.image_appliance = image_appliance

    def kiwi_is_available(self):
        (lines, _stdout, _stderr) = run_command('source /build/venv/bin/activate; kiwi-ng -v')
        assert lines[-2].startswith('KIWI ')

    def berrymill_is_available(self):
        (_lines, stdout, _stderr) = run_command('source /build/venv/bin/activate; berrymill -h')
        assert 'usage: berrymill' in stdout

    def local_apt_repo(self):
        # generate signing key for repository
        run_command('gen_sign_key')
        (_lines, stdout, _stderr) = run_command('gpg --list-secret-keys')
        assert 'info@elektrobit.com' in stdout
        #delete old repo data
        run_command('rm -rf /build/results/packages/dists')
        # generate apt repository
        run_command('gen_app_apt_repo')
        (_lines, stdout, _stderr) = run_command('cat /build/results/packages/dists/local/Release')
        assert 'Suite: local' in stdout
        (lines, _stdout, _stderr) = run_command('file /build/results/packages/dists/local/InRelease')
        assert lines[-2].startswith('/build/results/packages/dists/local/InRelease: PGP signed message')
        (lines, _stdout, _stderr) = run_command('file /build/results/packages/dists/local/Release.key')
        assert lines[-2].startswith('/build/results/packages/dists/local/Release.key: OpenPGP Public Key Version 4')
        (_lines, stdout, _stderr) = run_command('sudo apt update')
        assert 'file:/build/results/packages local' in stdout

    def berrymill_box_build(self):
        # delete old result
        run_command('rm -rf /build/results/images/qemu_crinit_x86_64')
        # build image
        run_command('box_build_image qemu-crinit-x86_64/appliance.kiwi')
        (lines, _stdout, _stderr) = run_command('file /build/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.qcow2')
        assert 'QEMU QCOW2 Image' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.qcow2')
        assert 'QEMU QCOW2 Image' in lines[-2]

    def berrymill_cross_build(self):
        # delete old result
        run_command('rm -rf /build/results/images/qemu_crinit_aarch64')
        # build image
        run_command('cross_build_image qemu-crinit-aarch64/appliance.kiwi')
        (lines, _stdout, _stderr) = run_command('file /build/results/images/qemu_crinit_aarch64/qemu_crinit_aarch64.*.qcow2')
        assert 'QEMU QCOW2 Image' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/qemu_crinit_aarch64/qemu_crinit_aarch64.*.qcow2')
        assert 'QEMU QCOW2 Image' in lines[-2]

    def berrymill_kvm_build(self):
        # delete old result
        run_command('rm -rf /build/results/images/qemu_crinit_x86_64')
        # build image
        run_command('kvm_build_image qemu-crinit-x86_64/appliance.kiwi')
        (lines, _stdout, _stderr) = run_command('file /build/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.qcow2')
        assert 'QEMU QCOW2 Image' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.qcow2')
        assert 'QEMU QCOW2 Image' in lines[-2]

    def berrymill_kvm_sysroot(self):
        # delete old result
        run_command('rm -rf /build/results/images/qemu_crinit_x86_64')
        # build image
        run_command('kvm_build_image qemu-crinit-x86_64/appliance_sysroot.kiwi')
        (lines, _stdout, _stderr) = run_command('file /build/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.tar.xz')
        assert 'XZ compressed data' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/qemu_crinit_x86_64/qemu_crinit_x86_64.*.tar.xz')
        assert 'XZ compressed data' in lines[-2]

    def berrymill_cross_sysroot(self):
        # delete old result
        run_command('rm -rf /build/results/images/qemu_crinit_aarch64')
        # build image
        run_command('cross_build_image qemu-crinit-aarch64/appliance_sysroot.kiwi')
        (lines, _stdout, _stderr) = run_command('file /build/results/images/qemu_crinit_aarch64/qemu_crinit_aarch64.*.tar.xz')
        assert 'XZ compressed data' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/qemu_crinit_aarch64/qemu_crinit_aarch64.*.tar.xz')
        assert 'XZ compressed data' in lines[-2]

    def berrymill_cross_build_image(self):
        # delete old result
        run_command(f'rm -rf /build/results/images/{self.image_name}')
        # build image
        run_command(f'cross_build_image {self.image_appliance}')
    
    def berrymill_kvm_build_image(self):
        print(f'Image: {self.image_name}')
        print(f'Appliance: {self.image_appliance}')
        # delete old result
        run_command(f'rm -rf /build/results/images/{self.image_name}')
        # build image
        run_command(f'kvm_build_image {self.image_appliance}')