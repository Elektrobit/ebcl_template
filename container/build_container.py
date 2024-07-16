""" Script to build the EBcL SDK container. """
import os
import logging
import subprocess
import yaml


class ContainerBuilder:
    """ ContainerBuilder builds and EBcL SDK dev container.  """

    def __init__(self):
        self.config = None
        self.build_tool = None
        self.base_container_name = None

    def load_config(self, file="build_config.yaml") -> None:
        """ Load container configuration from config file.

        Args:
            file (str, optional): Path to the container configuration.
                Defaults to "build_config.yaml".
        """
        with open(file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        logging.info('Conifg: %s', self.config)

    def _set_builder(self) -> None:
        """ Get the build tool form the environment. """
        if 'BUILDER' in os.environ:
            self.build_tool = os.environ['BUILDER']
        else:
            self.build_tool = 'docker'
        logging.info('Builder: %s', self.build_tool)

    def _build_container(self, name: str, path: str) -> None:
        """ Build a container layer. """
        logging.info('Building layer %s.', name)
        command = f'{self.build_tool} build -t {name} '\
            f'--build-arg BASE_CONTAINER_NAME="{self.base_container_name}" {path}'
        logging.debug('Command: %s', command)
        subprocess.run(command, shell=True, check=True)

    def _tag_container(self) -> None:
        """ Tag a container. """
        repo = self.config['Repository']
        basename = self.config['Base-Name']
        version = self.config['Version']
        tag = f'{repo}/{basename}:{version}'

        logging.info('Tagging container %s as %s.', self.base_container_name, tag)

        command = f'{self.build_tool} tag {self.base_container_name} {tag}'
        subprocess.run(command, shell=True, check=True)

    def _get_container_name(self, path: str) -> str:
        """ Build the container name. """
        repo = self.config['Repository']
        basename = self.config['Base-Name']
        name = os.path.basename(path)
        version = self.config['Version']
        return f'{repo}/{basename}_{name}:{version}'

    def build_container(self):
        """ Build the dev container. """
        self._set_builder()
        self.base_container_name = self.config['Base-Container']

        for path in self.config['Layers']:
            container_name = self._get_container_name(path)
            self._build_container(container_name, path)
            self.base_container_name = container_name

        self._tag_container()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    builder = ContainerBuilder()
    builder.load_config()
    builder.build_container()
