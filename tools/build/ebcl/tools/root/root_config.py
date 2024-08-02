#!/usr/bin/env python
""" EBcL root filesystem config helper. """
import argparse
import logging
import os
import tempfile

from ebcl.common.config import load_yaml
from ebcl.common.fake import Fake
from ebcl.common.files import Files, EnvironmentType, parse_scripts


class RootConfig:
    """ EBcL root filesystem config helper. """

    # TODO: test

    # config file
    config: str
    # config values
    scripts: list[dict[str, str]]
    # fakeroot helper
    fake: Fake
    # files helper
    fh: Files

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        config = load_yaml(config_file)

        self.config = config_file

        self.scripts = config.get('scripts', [])
        self.scripts = parse_scripts(config.get('scripts', None))

        self.fake = Fake()
        self.files = Files(self.fake)

    def _run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            logging.info('Running script: %s', script)

            for script in self.scripts:
                logging.info('Running script %s.', script)

                file = os.path.join(os.path.dirname(
                    self.config), script['name'])

                self.fh.run_script(
                    file=file,
                    params=script.get('params', None),
                    environment=EnvironmentType.from_str(
                        script.get('env', None))
                )

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
