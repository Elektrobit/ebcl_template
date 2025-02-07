# pylint: disable=invalid-name
"""
Abstraction layer for power management.
"""
import logging
import os

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
                self.interface = PowerQemu()
            case "QEMU_EXPLICT_OPTION":
                qemu_cmd = os.getenv('EBCL_QEMU_CMDLINE', '')
                if qemu_cmd == '':
                    raise ValueError(
                        "QEMU_EXPLICT_OPTION specified but no qemu command given")
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
