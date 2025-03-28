from logging import Logger

from .log_system import LogSystem
from .storge_system import BaseConfig, Field, ConfigError


class Config(BaseConfig):
    # ---------- [语言设置] ----------
    language: str = Field(default="", description="界面显示语言 en_us/zh_cn")

    # ---------- [UI设置] ----------
    light_mode: str = Field(default="Auto", description="明亮模式选项 Auto/Light/Dark")
    vague_mode: bool = Field(default=True, description="是否启用模糊效果")
    animation: bool = Field(default=True, description="是否启用动画效果")

    # ---------- [Nexusmods] ----------
    uuid: str = Field(default="", description="网站用户名")
    connection_token: str = Field(default="", description="网站Token")
    api: str = Field(default="", description="API密钥（从nexusmods获取）")

    # ---------- [游戏路径] ----------
    game_path: str = Field(default="", description="游戏安装根目录路径")

    # ---------- [RE框架] ----------
    installed_ref_version: str = Field(default="", description="已安装的RE框架版本")

    # ---------- [Github] ----------
    proxy_mode: bool = Field(default=False, description="Github 是否启用代理")
    proxy_url: str = Field(
        default="https://api-gh.muran.eu.org/",
        description="代理服务器地址（示例：https://ghproxy.com/）",
    )

    # ---------- [MOD管理] ----------
    installed_mods: dict = Field(default={}, description="已安装的MOD列表（自动维护）")


class GlobalContext(object):
    def __init__(self, debug: bool):
        global _log_system, _config
        _log_system = LogSystem(debug=debug)
        try:
            _config = Config.load()
        except ConfigError as e:
            _log_system.logger.error(f"配置操作失败: {str(e)}")

    @staticmethod
    def get_logger() -> Logger:
        return _log_system.logger

    @staticmethod
    def get_config() -> Config:
        return _config
