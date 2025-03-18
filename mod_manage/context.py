from logging import Logger

from mod_manage import LogSystem, BaseConfig, Field, ConfigError


class Config(BaseConfig):
    # ---------- [语言设置] ----------
    #: 界面显示语言 en_us/zh_cn
    language: str = Field(default="", description="界面显示语言 en_us/zh_cn")

    # ---------- [UI设置] ----------
    #: 明亮模式选项 Auto/Light/Dark
    light_mode: str = Field(default="Auto", description="明亮模式选项 Auto/Light/Dark")
    #: 是否启用模糊效果
    vague_mode: bool = Field(default=True, description="是否启用模糊效果")
    #: 是否启用动画效果
    animation: bool = Field(default=True, description="是否启用动画效果")

    # ---------- [Nexusmods] ----------
    #: API密钥（从nexusmods获取）
    api: str = Field(default="", description="API密钥（从nexusmods获取）")
    #: 网站用户名
    username: str = Field(default="", description="网站用户名")

    # ---------- [游戏路径] ----------
    #: 游戏安装根目录路径
    game_path: str = Field(default="", description="游戏安装根目录路径")

    # ---------- [REF框架] ----------
    #: 已安装的REF框架版本
    installed_rf_version: str = Field(default="", description="已安装的REF框架版本")

    # ---------- [Github] ----------
    #: 是否启用代理
    proxy_mode: bool = Field(default=False, description="Github 是否启用代理")
    #: 代理服务器地址（示例：https://ghproxy.com/）
    proxy_url: str = Field(
        default="https://api-gh.muran.eu.org/",
        description="代理服务器地址（示例：https://ghproxy.com/）",
    )

    # ---------- [MOD管理] ----------
    #: 已安装的MOD列表（自动维护）
    installed_mods: dict = Field(default={}, description="已安装的MOD列表（自动维护）")


class GlobalContext(object):
    def __init__(self, debug: bool):
        global log_system, config
        log_system = LogSystem(debug=debug)
        try:
            config = Config.load()
        except ConfigError as e:
            log_system.logger.error(f"配置操作失败: {str(e)}")

    @staticmethod
    def get_logger() -> Logger:
        return log_system.logger

    @staticmethod
    def get_config() -> Config:
        return config
