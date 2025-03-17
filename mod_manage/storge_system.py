import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Type
import tempfile


class ConfigError(Exception):
    """配置文件异常基类"""

    pass


class ConfigValidationError(ConfigError):
    """配置校验失败异常"""

    pass


class ConfigFileNotFound(ConfigError):
    """配置文件不存在异常"""

    pass


class JSONConfig(object):
    def __init__(
        self,
        file_path: str,
        default_config: Optional[Dict] = None,
        schema: Optional[Dict[str, Type]] = None,
        version: str = "0"
    ):
        """
        初始化配置管理器

        :param file_path: 配置文件路径
        :param default_config: 默认配置（当文件不存在时自动创建）
        :param schema: 配置校验模式字典 {key: type}
        """
        from mod_manage import get_variable

        self.log_system = get_variable("log_system")

        self.file_path = Path(file_path).expanduser().resolve()
        self.default_config = default_config or {}
        self.schema = schema or {}
        self._data = {}

        self.version = version
        self._data["__version__"] = version

        # 自动创建父目录
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict:
        """加载配置文件"""
        try:
            if not self.file_path.exists():
                if self.default_config:
                    self._data = self.default_config.copy()
                    self._save()
                    return self._data
                raise ConfigFileNotFound(f"配置文件 {self.file_path} 不存在")

            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)

            self._validate()
            return self._data.copy()
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件解析失败: {str(e)}") from e

    def save(self, custom_data: Optional[Dict] = None) -> None:
        """保存配置文件（原子写入）"""
        try:
            data = custom_data or self._data
            self._validate(data)

            # 使用临时文件实现原子写入
            with tempfile.NamedTemporaryFile(
                mode="w", dir=self.file_path.parent, delete=False, encoding="utf-8"
            ) as tmp_file:
                json.dump(data, tmp_file, indent=4, ensure_ascii=False)

            # 替换原文件
            os.replace(tmp_file.name, self.file_path)
        except (IOError, OSError) as e:
            if tmp_file.name:
                try:
                    os.unlink(tmp_file.name)
                except OSError:
                    pass
            raise ConfigError(f"保存配置文件失败: {str(e)}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持点分隔符）"""
        keys = key.split(".")
        value = self._data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, auto_save: bool = False) -> None:
        """设置配置项（支持点分隔符）"""
        keys = key.split(".")
        current = self._data

        for i, k in enumerate(keys[:-1]):
            if k not in current:
                current[k] = {}
            current = current[k]
            if not isinstance(current, dict):
                raise ConfigError(f"无效的配置路径: {key}")

        last_key = keys[-1]
        current[last_key] = value

        if auto_save:
            self.save()

    def check_version(self):
        """检查并执行版本迁移"""
        file_version = self._data.get("__version__", "0")

        if file_version != self.current_version:
            self.log_system.logger.debug(
                f"检测到配置版本变化 ({file_version} -> {self.current_version})"
            )
            self.migrate(file_version)
            self._data["__version__"] = self.current_version
            self.save()

    def migrate(self, from_version: str):
        """执行版本迁移"""
        # 创建备份（重要！）
        backup_path = self.file_path.with_suffix(".bak")
        shutil.copyfile(self.file_path, backup_path)
        self.log_system.logger.debug(f"已创建备份文件: {backup_path}")

        # 版本升级路线图
        migration_path = {}

        # 逐步执行升级
        current_v = from_version
        while current_v in migration_path:
            migration_func = migration_path[current_v]
            new_version = migration_func()
            self.log_system.logger.debug(f"从 {current_v} 迁移到 {new_version}")
            current_v = new_version

    def _validate(self, data: Optional[Dict] = None) -> None:
        """配置数据校验"""
        data = data or self._data
        errors = []

        for key, expected_type in self.schema.items():
            value = self.get(key)
            if not isinstance(value, expected_type):
                errors.append(f"配置项 '{key}' 类型错误，应为 {expected_type.__name__}")

        if errors:
            raise ConfigValidationError("\n".join(errors))

    def _save(self) -> None:
        """内部保存方法（首次创建时使用）"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
        except (IOError, OSError) as e:
            raise ConfigError(f"创建配置文件失败: {str(e)}") from e

    @property
    def data(self) -> Dict:
        """返回配置数据的副本"""
        return self._data.copy()


if __name__ == "__main__":
    # 使用示例
    config_schema = {"database.host": str, "database.port": int, "debug": bool}

    default_config = {
        "database": {"host": "localhost", "port": 3306, "user": "admin"},
        "debug": False,
    }

    try:
        # 初始化配置管理器
        config = JSONConfig(
            file_path="~/myapp/config.json",
            default_config=default_config,
            schema=config_schema,
        )

        # 加载配置
        config.load()

        # 获取配置项
        print("当前数据库端口:", config.get("database.port"))

        # 修改配置
        config.set("database.port", 3307)
        config.set("new_feature.enabled", True)

        # 保存配置
        config.save()

        # 类型校验示例（会抛出异常）
        # config.set("debug", "true")  # 错误类型
        # config.save()

    except ConfigError as e:
        print(f"配置操作失败: {str(e)}")
