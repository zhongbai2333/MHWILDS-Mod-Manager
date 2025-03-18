import sys

global log_system, config


def _start_cli_program() -> None:
    from mod_manage import i18n, t
    if not config.language:
        match input("Press Language: [ZH_CN/en_us] "):
            case "zh_cn":
                lang = "zh_cn"
            case "en_us":
                lang = "en_us"
            case "":
                lang = "zh_cn"
            case _:
                log_system.warning("Unknown Language!")
                return
        config.language = lang
        i18n.set_language(lang)
        config.save()
        log_system.info(t("welcome.choose_language"))
    else:
        i18n.set_language(config.language)
    log_system.info(t("welcome.welcome_cli"))
    while True:
        log_system.info(t("cli.menu"))
        match input(t("cli.wait_press")):
            case 1:
                match input(t("cli.ref_menu")):
                    case _:
                        log_system.warning(t("cli.unknown_num"))
            case _:
                log_system.warning(t("cli.unknown_num"))


def get_help() -> None:
    pass


def main(core: bool = False) -> None:
    """核心主程序"""
    from mod_manage import GlobalContext

    global log_system, config

    log_system = GlobalContext.get_logger()
    config = GlobalContext.get_config()

    log_system.info("Core Started.")
    log_system.debug("Debug information is being displayed.")

    if core:
        try:
            _start_cli_program()
        except KeyboardInterrupt:
            log_system.info("Core Exited.")
            sys.exit(0)
