# pylint: disable=invalid-name
"""
Abstraction layer for power management.
"""
import logging

from typing import Any

from interfaces.power_qemu import PowerQemu # type: ignore[import-untyped]


class Power:
    """
    Power provides a generic power management interface.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self, mode="QEMU") -> None:
        logging.basicConfig(level=logging.DEBUG)

        logging.info('Setting up CommManager with interface %s...', mode)

        self.mode = mode
        match mode:
            case "QEMU":
                self.interface = PowerQemu()
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")

    def power_on(self, path: str) -> Any:
        """
        Run the image.
        """
        return self.interface.power_on(path)

    def power_off(self):
        """
        Stop the image by "power-cut".
        """
        self.interface.power_off()
