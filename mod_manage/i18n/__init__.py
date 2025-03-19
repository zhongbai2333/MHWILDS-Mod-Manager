import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class I18NManager:
    def __init__(self):
        self.is_frozen = getattr(sys, "frozen", False)

        # 修正路径到 lang 目录
        if self.is_frozen:
            self.base_dir = Path(sys._MEIPASS) / "mod_manage"
        else:
            # 确保路径指向项目根目录下的 mod_manage/lang
            self.base_dir = Path(__file__).resolve().parent.parent.parent / "mod_manage"

        self.lang_dir = self.base_dir / "lang"  # 确保指向 lang 目录
        self._current_lang = "zh_cn"  # 保持全小写
        self._translations = {}
        self._fallback_lang = "en_us"  # 保持全小写

        # 初始化时立即加载语言文件
        self.set_language(self._current_lang)

    def set_language(self, lang_code: str) -> None:
        """统一转换为小写处理文件名"""
        lang_code = lang_code.lower()
        if self._load_lang_file(lang_code):
            self._current_lang = lang_code
        else:
            print(f"Failed to load {lang_code}, fallback to {self._fallback_lang}")
            self._load_lang_file(self._fallback_lang)
            self._current_lang = self._fallback_lang

    def _load_lang_file(self, lang_code: str) -> bool:
        """修复路径处理逻辑"""
        lang_code = lang_code.lower()  # 统一小写
        lang_path = self.lang_dir / f"{lang_code}.yml"

        print(f"Trying to load language file from: {lang_path}")  # 调试信息

        try:
            if lang_path.exists():
                with open(lang_path, "r", encoding="utf-8") as f:
                    self._translations = yaml.safe_load(f)
                return True
            else:
                # 打包环境备用加载方式
                if self.is_frozen:
                    frozen_path = (
                        Path(sys._MEIPASS) / "mod_manage" / "lang" / f"{lang_code}.yml"
                    )
                    if frozen_path.exists():
                        with open(frozen_path, "r", encoding="utf-8") as f:
                            self._translations = yaml.safe_load(f)
                        return True
                return False
        except Exception as e:
            print(f"Error loading language file: {e}")
            return False

    def get(self, key: str, **kwargs) -> str:
        """
        获取翻译文本
        :param key: 翻译键（使用点号分隔，例如 "ui.welcome"）
        :param kwargs: 格式化参数
        """
        parts = key.split(".")
        current = self._translations

        try:
            for part in parts:
                current = current[part]
        except KeyError:
            return f"[Missing translation: {key}]"

        # 处理多行文本的缩进
        if isinstance(current, list):
            return "\n".join(current)

        # 格式化文本
        if kwargs and isinstance(current, str):
            return current.format(**kwargs)

        return str(current)

    def reload(self) -> None:
        """重新加载当前语言文件"""
        self._load_lang_file(self._current_lang)


# 全局单例实例
i18n = I18NManager()


def set_language(lang_code: str) -> None:
    i18n.set_language(lang_code.lower())  # 统一小写处理


def t(key: str, **kwargs) -> str:
    return i18n.get(key, **kwargs)
