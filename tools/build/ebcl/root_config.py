#!/usr/bin/env python
""" EBcL root filesystem config helper. """
import argparse
import logging
import os
import tempfile

from .config import load_yaml
from .fake import Fake
from .files import Files, EnvironmentType


class RootConfig:
    """ EBcL root filesystem config helper. """
    # config file
    config: str
    # config values
    scripts: list[dict[str, str]]
    # fakeroot helper
    fake: Fake
    # files helper
    files: Files

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        config = load_yaml(config_file)

        self.config = config_file

        self.scripts = config.get('scripts', [])

        self.fake = Fake()
        self.files = Files(self.fake)

    def _run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            script_path = script['name']

            params = ''
            if 'params' in script:
                params = script['params']

            env = EnvironmentType.FAKEROOT
            if 'env' in script:
                e = EnvironmentType.from_str(script['env'])
                if e:
                    env = e
                else:
                    logging.error(
                        'Unknown environment %s for script %s!', script['env'], script['name'])

            script_file = os.path.abspath(os.path.join(
                os.path.dirname(self.config), script_path))

            logging.info('Running script %s in env %s', script, env)

            if not os.path.isfile(script_file):
                logging.error('Script %s not found!', script)
                continue

            res = self.files.run_script(script_file, params, env)
            if not res:
                logging.error('Execution of script %s failed!', script_file)

    def config_root(self, archive_in: str, archive_out: str) -> None:
        """ Config the tarball.  """
        if not os.path.exists(archive_in):
            logging.critical('Archive %s does not exist!', archive_in)
            return

        if self.scripts:
            with tempfile.TemporaryDirectory() as tmp_root_dir:
                self.files.target_dir = tmp_root_dir
                self.files.extract_tarball(archive_in, tmp_root_dir)
                self._run_scripts()
                ao = self.files.pack_root_as_tarball(
                    output_dir=os.path.dirname(archive_out),
                    archive_name=os.path.basename(archive_out),
                    root_dir=tmp_root_dir
                )

                if not ao:
                    logging.critical('Repacking root failed!')
                    return


def main() -> None:
    """ Main entrypoint of EBcL root filesystem config helper. """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Configure the given root tarball.')
    parser.add_argument('config_file', type=str,
                        help='Path to the YAML configuration file')
    parser.add_argument('archive_in', type=str, help='Root tarball.')
    parser.add_argument('archive_out', type=str, help='New tarball.')

    args = parser.parse_args()

    logging.info('Running root_configurator with args %s', args)

    # Read configuration
    generator = RootConfig(args.config_file)

    # Create the boot.tar
    generator.config_root(args.archive_in, args.archive_out)


if __name__ == '__main__':
    main()
