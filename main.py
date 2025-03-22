import argparse
import sys

from mod_manage.constants import CORE_VERSION, UI_VERSION
from mod_manage.context import GlobalContext
from mod_manage.manage_core import core_main
from mod_manage.manage_ui import ui_main


def main():
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
        print(f"MHWilds Mod Manager - Core v{CORE_VERSION} - UI v{UI_VERSION}")
        sys.exit(0)

    # 主逻辑分发
    debug_mode = args.debug
    GlobalContext(debug_mode)

    if args.core:
        # 纯命令行模式
        core_main(core=args.core)
    else:
        # 默认混合模式
        core_main()
        ui_main()
