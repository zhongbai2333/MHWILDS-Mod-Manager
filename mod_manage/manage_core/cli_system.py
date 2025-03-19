import sys

from ..context import GlobalContext
from ..i18n import i18n, t


class CliSystem(object):
    def __init__(self):
        self.log_system = GlobalContext.get_logger()
        self.config = GlobalContext.get_config
        # 配置语言
        if not self.config.language:
            self._setup_lang()
        else:
            i18n.set_language(self.config.language)
        self._start_cli_program()

    def _setup_lang(self):
        """初始化语言"""
        match input("Press Language: [ZH_CN/en_us] "):
            case "zh_cn":
                lang = "zh_cn"
            case "en_us":
                lang = "en_us"
            case "":
                lang = "zh_cn"
            case _:
                self.log_system.warning("Unknown Language!")
                sys.exit(0)
        self.config.language = lang
        i18n.set_language(lang)
        self.config.save()
        self.log_system.info(t("welcome.choose_language"))

    def _start_cli_program(self) -> None:
        """开始命令行程序"""
        self.log_system.info(t("welcome.welcome_cli"))
        command_list = {
            "1": self._ref_manage,
            "2": self._game_manage,
            "3": self._nexus_manage,
            "4": self._mod_manage,
        }
        while True:
            self.log_system.info(t("cli.menu"))
            num = input(t("cli.wait_press"))
            if num in command_list.keys():
                command_list[num]()
            else:
                self.log_system.warning(t("cli.unknown_num"))

    def _ref_manage(self) -> None:
        self.log_system.info(t("cli.ref_menu"))
        pass

    def _game_manage(self) -> None:
        pass

    def _nexus_manage(self) -> None:
        pass

    def _mod_manage(self) -> None:
        pass
