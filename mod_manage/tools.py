import os
import time
import ctypes
import threading
import functools
from typing import Optional, Union, Callable

from .i18n import t


class FunctionThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True  # 确保线程为守护线程


def new_thread(arg: Optional[Union[str, Callable]] = None):
    """
    启动一个新的线程运行装饰的函数，同时支持类方法和普通函数。
    """

    def wrapper(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            # 检查是否是类方法
            if len(args) > 0 and hasattr(args[0], func.__name__):
                # 将未绑定方法绑定到实例
                bound_func = func.__get__(args[0])
            else:
                # 普通函数
                bound_func = func

            # 创建线程
            thread = FunctionThread(
                target=bound_func, args=args, kwargs=kwargs, name=thread_name
            )
            thread.start()
            return thread

        wrap.original = func  # 保留原始函数
        return wrap

    if isinstance(arg, Callable):  # @new_thread 用法
        thread_name = None
        return wrapper(arg)
    else:  # @new_thread(...) 用法
        thread_name = arg
        return wrapper


def auto_trigger(interval: float, thread_name: Optional[str] = None):
    """
    创建一个自动触发的装饰器。

    Args:
        interval (float): 触发间隔时间（秒）。
        thread_name (Optional[str]): 线程名称，默认为函数名。

    Returns:
        Callable: 装饰后的函数。
    """

    def decorator(func: Callable):
        stop_event = threading.Event()

        def trigger_loop(instance=None, *args, **kwargs):
            while not stop_event.is_set():
                if instance:
                    wrapped_func = new_thread(thread_name)(func.__get__(instance))
                else:
                    wrapped_func = new_thread(thread_name)(func)
                wrapped_func(*args, **kwargs)
                time.sleep(interval)

        @new_thread(f"{thread_name or func.__name__}_trigger_loop")
        def start_trigger(instance=None, *args, **kwargs):
            trigger_thread = threading.Thread(
                target=trigger_loop,
                args=(instance,) + args,
                kwargs=kwargs,
                name=thread_name,
                daemon=True,
            )
            trigger_thread.start()
            return trigger_thread

        def stop():
            stop_event.set()

        start_trigger.stop = stop
        return start_trigger

    return decorator


def get_available_drives():
    """获取系统中所有存在的驱动器盘符"""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if bitmask & 1:
            drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives


def find_steam_game_path(game_name="MonsterHunterWilds"):
    """
    查找 Steam 游戏的安装路径
    返回找到的第一个有效路径，如果没有找到则返回 None
    """
    # 检查所有驱动器的 SteamLibrary 路径
    for drive in get_available_drives():
        possible_path = os.path.join(
            drive, "SteamLibrary", "steamapps", "common", game_name
        )
        if os.path.exists(possible_path):
            return os.path.normpath(possible_path)

    # 检查默认 Steam 安装路径
    default_locations = [
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Steam"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Steam"),
    ]

    for location in default_locations:
        possible_path = os.path.join(location, "steamapps", "common", game_name)
        if os.path.exists(possible_path):
            return os.path.normpath(possible_path)

    return None


def validate_game_path(input_path):
    """
    验证游戏路径是否有效（包含MonsterHunterWilds.exe）
    返回包含验证结果的字典

    :param input_path: 用户输入的路径
    :return: {
        "is_valid": bool,
        "error_code": int,
        "message": str,
        "normalized_path": str
    }
    """
    # 错误代码定义：
    # 0 = 有效路径
    # 1 = 路径不存在
    # 2 = 路径不是目录
    # 3 = 缺少可执行文件

    # 路径规范化处理
    normalized_path = os.path.normpath(input_path.strip())
    result = {
        "is_valid": False,
        "error_code": -1,
        "message": "",
        "normalized_path": normalized_path,
    }

    # 基础路径验证
    if not os.path.exists(normalized_path):
        result.update({"error_code": 1, "message": t("core.game_error_path")})
        return result

    if not os.path.isdir(normalized_path):
        result.update({"error_code": 2, "message": t("core.game_error_not_folder")})
        return result

    # 检查可执行文件
    exe_path = os.path.join(normalized_path, "MonsterHunterWilds.exe")
    if not os.path.isfile(exe_path):
        result.update({"error_code": 3, "message": t("core.game_error_not_game_path")})
        return result

    # 所有验证通过
    result.update(
        {"is_valid": True, "error_code": 0, "message": t("core.game_success")}
    )
    return result
