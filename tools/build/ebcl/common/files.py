""" Files and scripts helpers. """
import glob
import logging
import os

from enum import Enum
from io import BufferedWriter
from pathlib import Path
from typing import Optional, Tuple, Any

from .fake import Fake


class EnvironmentType(Enum):
    """ Enum for supported script types. """
    FAKEROOT = 1
    FAKECHROOT = 2
    CHROOT = 3

    @classmethod
    def from_str(cls, script_type: Optional[str]):
        """ Get ImageType from str. """
        if not script_type:
            return cls.FAKEROOT

        if script_type == 'fake':
            return cls.FAKEROOT
        elif script_type == 'chfake':
            return cls.FAKECHROOT
        elif script_type == 'chroot':
            return cls.CHROOT
        else:
            return None

    def __str__(self) -> str:
        if self.value == 1:
            return "fake"
        elif self.value == 2:
            return "chfake"
        elif self.value == 3:
            return "chroot"
        else:
            return "UNKNOWN"


class Files:
    """ Files and scripts helpers. """
    # TODO: test

    target_dir: Optional[str]
    fake: Fake

    def __init__(self, fake: Fake, target_dir: Optional[str] = None) -> None:
        self.target_dir = target_dir
        self.fake = fake

    def copy_file(
        self,
        src: str,
        dst: str,
        environment: Optional[EnvironmentType] = EnvironmentType.FAKEROOT,
        uid: Optional[int] = None,
        gid: Optional[int] = None,
        mode: Optional[str] = None,
        move: bool = False,
        delete_if_exists: bool = False
    ) -> list[str]:
        """ Copy file or dir to target environment"""
        files: list[str] = []

        dst = os.path.abspath(dst)

        matches = glob.glob(src)

        for file in matches:
            file = os.path.abspath(file)

            if os.path.isfile(file) and os.path.isdir(dst):
                target = os.path.join(dst, os.path.basename(file))
            else:
                target = dst

            # TODO: test

            if file != target:
                fn_run = self.fake.run
                if environment == EnvironmentType.CHROOT:
                    fn_run = self.fake.run_sudo
                elif environment is None:
                    fn_run = self.fake.run_no_fake

                if os.path.isfile(file):
                    parent_dir = os.path.dirname(file)
                    fn_run(f'mkdir -p {parent_dir}')

                if delete_if_exists:
                    if os.path.exists(target):
                        fn_run(f'rm -rf {target}')

                if move:
                    fn_run(f'mv {file} {target}')
                else:
                    fn_run(f'cp -R {file} {target}')

                if uid:
                    fn_run(f'chown {uid} {target}')
                if gid:
                    fn_run(f'chown :{gid} {target}')
                if mode:
                    fn_run(f'chmod {mode} {target}')

            else:
                logging.debug(
                    'Not copying %s, source and destionation are identical.')

            files.append(target)

        return files

    def run_command(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        stdout: Optional[BufferedWriter] = None,
        check=True,
        environment: EnvironmentType = EnvironmentType.FAKEROOT
    ) -> Optional[Tuple[Optional[str], str, int]]:
        """ Run command. """
        target_dir: Optional[str] = None

        if not self.target_dir:
            if cwd:
                logging.info(
                    'Target dir not set, using cwd %s as fall-back.', cwd)
                target_dir = cwd
            else:
                logging.error('Target dir not set!')
                return None
        else:
            target_dir = self.target_dir

        if environment == EnvironmentType.FAKEROOT:
            return self.fake.run(
                cmd=cmd,
                cwd=cwd,
                stdout=stdout,
                check=check
            )

        fn_run = None

        if environment == EnvironmentType.FAKECHROOT:
            fn_run = self.fake.run_chroot
        elif environment == EnvironmentType.CHROOT:
            fn_run = self.fake.run_sudo_chroot

        assert fn_run is not None

        return fn_run(
            cmd=cmd,
            chroot=target_dir,
            check=check
        )

    def run_script(
        self,
        file: str,
        params: Optional[str] = None,
        environment: Optional[EnvironmentType] = None
    ) -> Optional[Tuple[Optional[str], str, int]]:
        """ Run scripts. """
        if not params:
            params = ''

        if not environment:
            environment = EnvironmentType.FAKEROOT

        if not self.target_dir:
            logging.error('Target dir not set!')
            return None

        logging.debug('Copying scripts %s', file)

        script_files = self.copy_file(file, self.target_dir)

        logging.debug('Running scripts %s in environment %s',
                      script_files, environment)

        res = None

        for script_file in script_files:
            logging.info('Running script %s in environment %s',
                         script_file, environment)

            if not os.path.isfile(script_file):
                logging.error('Script %s not found!', script_file)
                return None

            if environment == EnvironmentType.FAKECHROOT or \
                    environment == EnvironmentType.CHROOT:
                script_file = f'./{os.path.basename(script_file)}'

            if logging.root.level == logging.DEBUG:
                # Generate some more infos
                self.run_command(
                    cmd='echo $PWD',
                    cwd=self.target_dir,
                    environment=environment,
                    check=False
                )
                self.run_command(
                    cmd='ls -lah .',
                    cwd=self.target_dir,
                    environment=environment,
                    check=False
                )
                self.run_command(
                    cmd=f'ls -lah {script_file}',
                    cwd=self.target_dir,
                    environment=environment,
                    check=False
                )

            res = self.run_command(
                cmd=f'{script_file} {params}',
                cwd=self.target_dir,
                environment=environment,
                check=False
            )

            if os.path.abspath(script_file) != os.path.abspath(file):
                # delete copied file
                fn_run = self.fake.run
                if environment == EnvironmentType.CHROOT:
                    fn_run = self.fake.run_sudo

                fn_run(f'rm -f {script_file}',
                       cwd=self.target_dir,
                       check=False)

        return res

    def extract_tarball(self, archive: str, directory: Optional[str] = None) -> Optional[str]:
        """ Extract tar archive to directory. """
        target_dir = self.target_dir

        if directory:
            target_dir = directory

        if not target_dir:
            logging.error('No target dir found!')
            return None

        tar_file = Path(archive)
        if not (tar_file.is_file() or tar_file.is_symlink()):
            logging.error('Archive is no file!')
            return None

        if tar_file.parent.absolute() != target_dir:
            dst = Path(target_dir) / tar_file.name
            self.fake.run(f'cp {tar_file.absolute()} {dst.absolute()}')
            tar_file = dst

        self.fake.run(f'tar xf {tar_file.name}', cwd=target_dir)

        return target_dir

    def pack_root_as_tarball(
        self,
        output_dir: str,
        archive_name: str = 'root.tar',
        root_dir: Optional[str] = None,
        use_fake_chroot: bool = True
    ) -> Optional[str]:
        """ Create tar archive of target_dir. """
        target_dir = self.target_dir

        if root_dir:
            target_dir = root_dir

        if not target_dir:
            logging.error('No target dir found!')
            return None

        tmp_archive = os.path.join(target_dir, archive_name)

        if os.path.isfile(tmp_archive):
            logging.info(
                'Archive %s exists. Deleting old archive.', tmp_archive)
            os.remove(tmp_archive)

        fn_run: Any = self.fake.run
        if use_fake_chroot:
            fn_run = self.fake.run_chroot

        fn_run(
            'tar --exclude=\'./proc/*\' --exclude=\'./sys/*\' --exclude=\'./dev/*\' '
            f'-cf {archive_name} .',
            target_dir
        )

        archive = os.path.join(output_dir, archive_name)

        if os.path.isfile(archive):
            logging.info('Archive %s exists. Deleting old archive.', archive)
            os.remove(archive)

        self.fake.run(f'mv {tmp_archive} {archive}')

        return archive


def parse_scripts(
    scripts: Optional[list[Any]],
    env: EnvironmentType = EnvironmentType.FAKEROOT
) -> list[dict[str, Any]]:
    """ Parse scripts config entry. """
    if not scripts:
        return []

    result: list[dict[str, Any]] = []

    for script in scripts:
        if isinstance(script, dict):
            if 'name' not in script:
                logging.error('Script %s has no name!', script)

            if 'env' not in script:
                script['env'] = env
            else:
                se = EnvironmentType.from_str(script['env'])
                logging.debug('Using env %s for script %s.', se, script)
                if se:
                    script['env'] = se
                else:
                    logging.error('Unknown environment type %s! '
                                  'Falling back to %s.', script, env)
                    script['env'] = env

            result.append(script)
        elif isinstance(script, str):
            logging.debug('Using default env %s for script %s.', env, script)
            result.append({
                'name': script,
                'env': env
            })
        else:
            logging.error('Unkown script entry type: %s', script)

    return result
