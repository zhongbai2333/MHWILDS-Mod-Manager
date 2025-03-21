import sys

from .ref_core import RefManage
from ..context import GlobalContext
from ..i18n import i18n, t


class CliSystem(object):
    def __init__(self):
        self._log_system = GlobalContext.get_logger()
        self._config = GlobalContext.get_config()
        self._ref_core = RefManage()
        # 配置语言
        if not self._config.language:
            self._setup_lang()
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
                self._log_system.warning("Unknown Language!")
                sys.exit(0)
        self._config.language = lang
        i18n.set_language(lang)
        self._config.save()
        self._log_system.info(t("welcome.choose_language"))

    def _start_cli_program(self) -> None:
        """开始命令行程序"""
        self._log_system.info(t("welcome.welcome_cli"))
        command_list = {
            "1": self._ref_manage,
            "2": self._game_manage,
            "3": self._nexus_manage,
            "4": self._mod_manage,
        }
        while True:
            self._log_system.info(t("cli.menu"))
            num = input(t("cli.wait_press"))
            if num in command_list.keys():
                command_list[num]()
            else:
                self._log_system.warning(t("cli.unknown_num"))

    def _ref_manage(self) -> None:
        """ref管理相关"""
        self._log_system.info(t("cli.ref_menu"))
        command_list = {"1": self._ref_release_page_manage}
        num = input(t("cli.wait_press")).split()
        if len(num) >= 1 and num[0] in command_list.keys():
            command_list[num[0]](num[1] if len(num) >= 2 else None)
        else:
            self._log_system.warning(t("cli.unknown_num"))

    def _ref_release_page_manage(self, page: str) -> None:
        """获取ref版本列表"""
        page = int(page) if page else 1
        releases_list = self._ref_core.get_release_list_page(5, page)
        for release in releases_list:
            self._log_system.info(
                t(
                    "cli.ref_info",
                    name=release[0],
                    version=release[1],
                    tag_name=release[2],
                    time=release[3],
                    url=release[4],
                )
            )
            self._log_system.info("=" * 80)
        all_pages = self._ref_core.get_release_list_all_page(5)
        command_list = {
            "p": self._ref_release_page_manage,
            "i": self._ref_install,
        }
        num = input(t("cli.ref_list_wait", page=page, all_pages=all_pages)).split()
        if len(num) >= 1 and num[0] in command_list.keys():
            command_list[num[0]](num[1] if len(num) >= 2 else None)
        else:
            self._log_system.warning(t("cli.unknown_num"))

    def _ref_install(self, version: str) -> None:
        """安装Ref框架确认步骤"""
        release = self._ref_core.search_release(version)
        self._log_system.info(
            t(
                "cli.ref_info",
                name=release[0],
                version=release[1],
                tag_name=release[2],
                time=release[3],
                url=release[4],
            )
        )
        command_list = {
            "y": self._ref_start_install,
            "n": self._ref_release_page_manage,
        }
        num = input(t("cli.ref_search_wait")).split()
        if len(num) >= 1 and num[0] in command_list.keys():
            command_list[num[0]](version if len(num) >= 2 and num[1] == "y" else "1")
        else:
            self._log_system.warning(t("cli.unknown_num"))
            self._ref_release_page_manage("1")

    def _ref_start_install(self, version: str) -> None:
        pass

    def _game_manage(self) -> None:
        pass

    def _nexus_manage(self) -> None:
        pass

    def _mod_manage(self) -> None:
        pass
