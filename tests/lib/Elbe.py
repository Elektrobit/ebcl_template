from utils import run_command

class Elbe:
    
    def elbe_is_available(self):
        (lines, _stdout, _stderr) = run_command('elbe --version')
        assert lines[-2].startswith('elbe v')

    def check_binfmt_works(self):
        (lines, _stdout, _stderr) = run_command('file /usr/bin/busybox')
        assert 'aarch64' in lines[-2]
        (_lines, stdout, _stderr) = run_command('busybox --help')
        assert 'Usage: busybox' in stdout

    def build_image_amd64(self):
        # delete old result
        run_command('rm -rf /build/results/images/ebcl-systemd-x86_64*', check=False, no_error=False)
        # build image
        run_command('build_image -i /tmp/build/images/elbe/qemu/systemd/ebcl-systemd-x86_64.xml')
        
        (lines, _stdout, _stderr) = run_command('file /build/results/images/ebcl-systemd-x86_64.xml/sdcard.img')
        assert 'sdcard.img: DOS/MBR boot sector' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /build/results/images/ebcl-systemd-x86_64.xml/initrd.img')
        assert 'initrd.img: ASCII cpio archive' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /build/results/images/ebcl-systemd-x86_64.xml/vmlinuz')
        assert 'Linux kernel x86' in lines[-2]

        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/ebcl-systemd-x86_64.xml/sdcard.img')
        assert 'sdcard.img: DOS/MBR boot sector' in lines[-2]
    
    def build_image_arm64(self):
        # delete old result
        run_command('rm -rf /build/results/images/ebcl-basic-image*', check=False, no_error=False)
        # build image
        run_command('build_image -i /tmp/build/images/elbe/qemu/crinit/ebcl-basic-image.xml')
        
        (lines, _stdout, _stderr) = run_command('file /build/results/images/ebcl-basic-image.xml/sdcard.img')
        assert 'sdcard.img: DOS/MBR boot sector' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /build/results/images/ebcl-basic-image.xml/initrd.img')
        assert 'Zstandard compressed data' in lines[-2]
        (lines, _stdout, _stderr) = run_command('file /build/results/images/ebcl-basic-image.xml/vmlinuz')
        assert 'gzip compressed data' in lines[-2]

        (lines, _stdout, _stderr) = run_command('file /workspace/results/images/ebcl-basic-image.xml/sdcard.img')
        assert 'sdcard.img: DOS/MBR boot sector' in lines[-2]

    def elbe_build_image(self, image_description: str, image_name: str):
        print(f'Image: {image_name}')
        print(f'Description: {image_description}')
        # delete old result
        run_command(f'rm -rf /build/results/images/{image_name}', check=False, no_error=False)
        # build image
        run_command(f'build_image -i {image_description}', check=False, no_error=False)
