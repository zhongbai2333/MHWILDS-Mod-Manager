import sys

from ..context import GlobalContext
from .cli_system import CliSystem

global log_system, config


def main(core: bool = False) -> None:
    """核心主程序"""

    global log_system, config

    log_system = GlobalContext.get_logger()
    config = GlobalContext.get_config()

    log_system.info("Core Started.")
    log_system.debug("Debug information is being displayed.")

    if core:
        try:
            CliSystem()
        except KeyboardInterrupt:
            log_system.info("Core Exited.")
            sys.exit(0)
