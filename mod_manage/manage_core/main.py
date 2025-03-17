import sys

log_system, config = None, None


def _start_cli_program() -> None:
    while True:
        pass


def main(debug: bool, core: bool = False) -> None:
    """核心主程序"""
    global log_system, config
    from mod_manage import get_variable

    log_system = get_variable("log_system")
    config = get_variable("config")

    log_system.logger.info("Core Started.")
    log_system.logger.debug("Debug Mode ON")

    if core:
        try:
            _start_cli_program()
        except KeyboardInterrupt:
            log_system.logger.info("Core Exited.")
            sys.exit(0)
