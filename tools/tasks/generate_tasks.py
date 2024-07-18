#!/usr/bin/python3
""" Script to generate the image related tasks. """
import json
import os
import logging
import yaml


class TaskGenerator:
    """ TaskGenerator generates VS Code build tasks for kiwi and elbe images.  """

    def __init__(self):
        self.config = None
        self.tasks = None

    def load_config(self, file='tasks.yaml') -> None:
        """ Load task configuration from config file.

        Args:
            file (str, optional): Path to the task configuration.
                Defaults to "tasks.yaml".
        """
        file = os.path.join(os.path.dirname(__file__), file)
        with open(file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        logging.info('Conifg: %s', self.config)

    def load_tasks(self, file='tasks.json'):
        """ Load the base tasks.json file. """
        file = os.path.join(os.path.dirname(__file__), file)
        with open(file, 'r', encoding='utf-8') as tasks_file:
            self.tasks = json.load(tasks_file)

    def _kiwi_build_image(self, name: str, appliance: str, cross=True) -> None:
        """ Add a kiwi image build task to the tasks list. """
        task = dict()
        task['type'] = 'shell'
        task['label'] = f'EBcL: Image {name}'
        if cross:
            task['command'] = 'cross_build_image'
        else:
            task['command'] = 'kvm_build_image'
        task['args'] = [appliance]
        task['group'] = {
            'kind': 'build',
            'isDefault': True
        }
        task['detail'] = f'Build the {name} image with kiwi.'

        self.tasks['tasks'].append(task)

    def _kiwi_build_sysroot(self, name: str, appliance: str, cross=True) -> None:
        """ Add a kiwi image build task to the tasks list. """
        task = dict()
        task['type'] = 'shell'
        task['label'] = f'EBcL: Sysroot {name}'
        if cross:
            task['command'] = 'cross_build_sysroot'
        else:
            task['command'] = 'kvm_build_sysroot'
        task['args'] = [appliance]
        task['group'] = {
            'kind': 'build',
            'isDefault': True
        }
        if cross:
            task['detail'] = f'Prepare sysroot aarch64 for the {name} image with kiwi.'
        else:
            task['detail'] = f'Prepare sysroot x86_64 for the {name} image with kiwi.'

        self.tasks['tasks'].append(task)

    def _kiwi_run_image(self, name: str, cross=True) -> None:
        """ Add a QEMU task to run the kiwi EFI image. """
        task = dict()
        task['type'] = 'shell'
        task['label'] = f'EBcL: Run QEMU {name}'
        if cross:
            task['command'] = 'qemu_efi_aarch64'
        else:
            task['command'] = 'qemu_efi_x86_64'

        image = name.replace('-', '_')
        image = f'{image}/{image}'
        if cross:
            image = f'{image}.aarch64-1.1.0-0.qcow2'
        else:
            image = f'{image}.x86_64-1.1.0-0.qcow2'

        task['args'] = [image]
        task['group'] = {
            'kind': 'build',
            'isDefault': True
        }
        task['detail'] = f'Run the {name} image in QEMU.'

        self.tasks['tasks'].append(task)

    def generate_kiwi_tasks(self):
        """ Generate build tasks for the kiwi images and sysroots. """
        if 'kiwi' in self.config:
            config = self.config['kiwi']
            extension = config['extension']
            sysroot_suffix = f"{config['sysroot suffix']}.kiwi"
            for folder in config['folders']:
                folder = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../{folder}'))
                for root, _dir, files in os.walk(folder):
                    name = os.path.basename(root)
                    for file in files:
                        if 'ignore' in config and file in config['ignore']:
                            logging.info('Skipping kiwi image %s.', name)
                            continue
                        appliance = f'{name}/{file}'
                        if file.endswith(sysroot_suffix):
                            if 'x86_64' in name:
                                self._kiwi_build_sysroot(name, appliance, cross=False)
                            else:
                                self._kiwi_build_sysroot(name, appliance, cross=True)
                        elif file.endswith(extension):
                            cross = True
                            if 'x86_64' in name:
                                cross = False
                            self._kiwi_build_image(name, appliance, cross)
                            self._kiwi_run_image(name, cross)

    def _elbe_build_image(self, name: str, description: str) -> None:
        """ Add a elbe image build task to the tasks list. """
        task = dict()
        task['type'] = 'shell'
        task['label'] = f'EBcL: Image {name}'
        task['command'] = 'build_image'
        task['args'] = [description]
        task['group'] = {
            'kind': 'build',
            'isDefault': True
        }
        task['detail'] = f'Build the {name} image with elbe.'

        self.tasks['tasks'].append(task)

    def _elbe_run_image(self, file: str) -> None:
        """ Add a QEMU task to run the elbe image. """
        task = dict()
        task['type'] = 'shell'
        task['label'] = f'EBcL: Run QEMU {file}'
        if 'x86_64' in file:
            task['command'] = 'qemu_aarch64'
        else:
            task['command'] = 'qemu_x86_64'
        image = f'/workspace/results/images/{file}/sdcard.img'
        task['args'] = [image]
        task['group'] = {
            'kind': 'build',
            'isDefault': True
        }
        task['detail'] = f'Run the {file} image in QEMU.'

        self.tasks['tasks'].append(task)

    def generate_elbe_tasks(self):
        """ Generate build tasks for the elbe images. """
        if 'elbe' in self.config:
            config = self.config['elbe']
            extension = config['extension']
            for folder in config['folders']:
                folder = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../{folder}'))
                logging.info('Processing elbe folder %s.', folder)
                for root, _dir, files in os.walk(folder):
                    path = os.path.abspath(os.path.join('/workspace/images', root))
                    for file in files:
                        if 'ignore' in config and file in config['ignore']:
                            logging.info('Skipping elbe file %s.', file)
                            continue
                        description = f'{path}/{file}'
                        if file.endswith(extension):
                            self._elbe_build_image(file, description)
                            self._elbe_run_image(file)

    def save_tasks(self):
        """ Update VS Code tasks file. """
        file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.vscode/tasks.json'))
        with open(file, 'w', encoding='utf-8') as tasks_file:
            json.dump(self.tasks, tasks_file, indent=4)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    generator = TaskGenerator()
    generator.load_config()
    generator.load_tasks()
    generator.generate_kiwi_tasks()
    generator.generate_elbe_tasks()
    generator.save_tasks()
