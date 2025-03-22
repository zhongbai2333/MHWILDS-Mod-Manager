import sys

from ..context import GlobalContext
from ..tools import find_steam_game_path
from .cli_system import CliSystem

global _log_system, _config


def main(core: bool = False) -> None:
    """核心主程序"""

    global _log_system, _config

    _log_system = GlobalContext.get_logger()
    _config = GlobalContext.get_config()

    if not _config.game_path:
        game_path = find_steam_game_path()
        _config.game_path = game_path if game_path else ""
        _config.save()

    _log_system.info("Core Started.")
    _log_system.debug("Debug information is being displayed.")

    if core:
        try:
            CliSystem()
        except KeyboardInterrupt:
            _log_system.info("Core Exited.")
            sys.exit(0)
