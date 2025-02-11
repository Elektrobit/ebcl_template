# pylint: disable=invalid-name
"""
Abstraction layer for power management.
"""
import logging
import os

import string
from typing import Any, Optional

from interfaces.power_qemu import PowerQemu # type: ignore[import-untyped]


class Power:
    """
    Power provides a generic power management interface.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

        self.mode = os.getenv('EBCL_TF_POWER_MODE', 'QEMU')

        logging.info('Setting up CommManager with interface %s...', self.mode)

        match self.mode:
            case "QEMU":
                qemu_cmd = ''
                if os.getenv('EBCL_QEMU_CMDLINE', ''):
                    qemu_cmd_expr = os.getenv('EBCL_QEMU_CMDLINE', '')
                    qemu_cmd = string.Template(qemu_cmd_expr).substitute(os.environ)
                    qemu_cmd = " ".join(qemu_cmd.split())
                    if qemu_cmd.strip() == '':
                        raise ValueError(
                            "Environment variable EBCL_QEMU_CMDLINE is not set in correct format")
                self.interface = PowerQemu(qemu_cmd=qemu_cmd)
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")

    def power_on(self, path: str, cmd: Optional[str] = None) -> Any:
        """
        Run the image.
        """
        return self.interface.power_on(path, cmd)

    def power_off(self, cmd: Optional[str] = None):
        """
        Stop the image by "power-cut".
        """
        self.interface.power_off(cmd)
