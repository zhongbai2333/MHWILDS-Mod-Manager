import time
import threading
import functools
from typing import Optional, Union, Callable


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
