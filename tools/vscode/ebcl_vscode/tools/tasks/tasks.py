#!/usr/bin/env python
""" Generate VS Code build tasks. """
import argparse
import json
import logging
import os

from typing import Optional, Any

from ebcl.common import init_logging, bug, promo
from ebcl.common.config import load_yaml


class TaskGenerator:
    """ Generate VS Code build tasks.  """

    # TODO: test

    tasks: Optional[dict[str, Any]]

    def __init__(self, config='tasks.yaml'):
        """ Load task configuration from config file. """
        self.config = config
        self.tasks = None

        self.config = load_yaml(config_file=config)
        logging.debug('Task conifg: %s', self.config)

    def load_tasks(self, file='tasks.json'):
        """ Load the base tasks.json file. """
        file = os.path.join(os.path.dirname(__file__), file)
        with open(file, 'r', encoding='utf-8') as tasks_file:
            self.tasks = json.load(tasks_file)

    def _add_task(self, name: str, command: str,
                  description: str, args: list[str]) -> None:
        """ Add a task to the tasks list. """
        task: dict[str, Any] = dict()
        task['type'] = 'shell'
        task['label'] = f'EBcL: {name}'
        task['command'] = command
        task['args'] = args
        task['group'] = {
            'kind': 'build',
            'isDefault': True
        }
        task['detail'] = description

        assert self.tasks

        self.tasks['tasks'].append(task)

    def generate_image_tasks(self):
        """ Generate build tasks for all images and sysroots. """
        assert self.config

        workspace = self.config.get('workspace', '/workspace')
        folders = self.config.get('folders', [])
        ignore = self.config.get('ignore', [])

        for folder in folders:
            folder = os.path.abspath(os.path.join(workspace, folder))

            if not os.path.isdir(folder):
                logging.error('Image folder %s not found!', folder)
                continue

            for root, _dir, files in os.walk(folder):
                if root in ignore:
                    continue

                for file in files:
                    if file != 'Makefile':
                        continue

                    file = os.path.join(root, file)

                    if file in ignore:
                        continue

                    name = os.path.relpath(file, folder).replace('/', '_')

                    tasks = [
                        {
                            'name': f'Image {name}',
                            'desc': f'Run the image build for {name}',
                            'args': ['image']
                        },
                        {
                            'name': f'Sysroot {name}',
                            'desc': f'Build and install the sysroot for {name}',
                            'args': ['sysroot_install']
                        }
                    ]

                    if '/qemu/' in file:
                        tasks.append({
                            'name': f'QEMU {name}',
                            'desc': f'Run {name} in QEMU'
                        })

                    for task in tasks:
                        self._add_task(
                            name=str(task['name']),
                            args=list(task.get('args', [])),
                            command='make',
                            description=str(task['desc'])
                        )

    def save_tasks(self):
        """ Update VS Code tasks file. """
        workspace = self.config.get('workspace', '/workspace')
        file = os.path.join(workspace, '.vscode/tasks.json')

        with open(file, 'w', encoding='utf-8') as tasks_file:
            json.dump(self.tasks, tasks_file, indent=4)

    def genenrate_tasks(self):
        """ Generate tasks.json. """
        self.load_tasks()
        self.generate_image_tasks()
        self.save_tasks()


def main() -> None:
    """ Main entrypoint of EBcL VS Code task generator. """
    init_logging()

    parser = argparse.ArgumentParser(
        description='Generate VS Code build task for images.')
    parser.add_argument('config', type=str,
                        help='Path to the YAML configuration file.')
    parser.add_argument('-o', '--output', type=str,
                        help='Path to the output directory')
    parser.add_argument('-t', '--template', type=str,
                        help='Template for tasks.json.')

    args = parser.parse_args()

    generator = TaskGenerator(args.config)

    try:
        generator.genenrate_tasks()
    except Exception as e:
        logging.critical('VS Code build task generation failed! %s', e)
        bug(bug_url='https://github.com/Elektrobit/ebcl_vscode_tools/issues')
        exit(1)

    promo()


if __name__ == '__main__':
    main()
