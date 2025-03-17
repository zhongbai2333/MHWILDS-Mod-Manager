import argparse
import sys

from mod_manage import *

if __name__ == "__main__":
    # 参数解析器配置
    parser = argparse.ArgumentParser(
        description="MHWilds Mod Manager",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    parser.add_argument("--debug", action="store_true", help="启用调试模式（详细输出）")
    parser.add_argument(
        "--core", action="store_true", help="启用纯命令行模式（禁用界面）"
    )
    parser.add_argument("--version", action="store_true", help="显示程序版本信息")
    parser.add_argument("-h", "--help", action="store_true", help="显示帮助信息并退出")

    # 参数解析
    args = parser.parse_args()

    # 处理系统参数
    if args.help:
        parser.print_help()
        sys.exit(0)

    if args.version:
        print(
            f"MHWilds Mod Manager - Core v{CORE_VERSION} - UI v{UI_VERSION}"
        )
        sys.exit(0)

    # 主逻辑分发
    debug_mode = args.debug
    log_system = LogSystem(debug=debug_mode)
    set_variable("log_system", log_system)

    config_schema = {
        "ui.light_mode": str,
        "ui.vague_mode": bool,
        "ui.animation": bool,
        "nexusmod.api": str,
        "nexusmod.username": str,
        "game.game_path": str,
        "ref.installed_rf_version": str,
        "github.proxy_mode": bool,
        "github.proxy_url": str,
        "mod.installed_mods": dict,
    }

    default_config = {
        "ui": {"light_mode": "Auto", "vague_mode": True, "animation": True},
        "nexusmod": {"api": "", "username": ""},
        "game": {"game_path": ""},
        "ref": {"installed_rf_version": ""},
        "github": {"proxy_mode": False, "proxy_url": "https://api-gh.muran.eu.org/"},
        "mod": {"installed_mods": {}},
    }

    try:
        config = JSONConfig(file_path="config.json", default_config=default_config, schema=config_schema, version=CONFIG_VERSION)
        config.load()
        set_variable("config", config)
    except ConfigError as e:
        log_system.logger.error(f"配置操作失败: {str(e)}")

    if args.core:
        # 纯命令行模式
        core_main(debug=debug_mode, core=args.core)
    else:
        # 默认混合模式
        core_main(debug=debug_mode)
        ui_main(debug=debug_mode)
