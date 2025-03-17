global_var = {}


def set_variable(key: str, value: any) -> None:
    """
    设置公共变量
    
    Args:
        key (str): 键名
        value (Any): 值
    """
    global global_var
    global_var[key] = value


def get_variable(key: str) -> any:
    """
    获取公共变量内容

    Args:
        key (str): 键名
    Returns:
        Any: 值
    """
    return global_var.get(key, None)


def del_variable(key: str) -> None:
    """
    删除指定键和内容
    
    Args:
        key (str): 键名
    """
    global_var.pop(key, None)
