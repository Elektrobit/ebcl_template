""" Template helpers. """
import logging
import os
import shutil

from typing import Any, Optional, Tuple

from jinja2 import Template


# TODO: test


def render_template(
        template_file: str,
        params: dict[str, Any],
        generated_file_name: str,
        results_folder: str,
        template_copy_folder: Optional[str] = None,
        write_generated_file: bool = True
) -> Tuple[Optional[str], Optional[str]]:
    """ Render the given template. """
    template_file = os.path.abspath(template_file)

    logging.debug('Rendering template %s', template_file)

    with open(template_file, encoding='utf8') as f:
        tmpl = Template(f.read())

    template_content = tmpl.render(**params)

    out_file = None
    if write_generated_file:
        out_file = os.path.join(results_folder, generated_file_name)

        logging.debug('Rendering result: %s', out_file)

        with open(out_file, 'w', encoding='utf8') as f:
            f.write(template_content)

    if template_copy_folder:
        # output template file
        template_copy = os.path.abspath(os.path.join(
            template_copy_folder, f'template.{generated_file_name}'))

        if template_file != template_copy:
            logging.debug('Copying template file as %s', template_copy)
            try:
                shutil.copy(template_file, template_copy)
            except Exception as e:
                logging.error('Copying template file %s to %s failed! %s',
                              template_file, template_copy, e)

    return (out_file, template_content)
