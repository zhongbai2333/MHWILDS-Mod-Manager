import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class I18NManager:
    def __init__(self):
        self._current_lang = "en_US"
        self._translations: Dict[str, Any] = {}
        self._fallback_lang = "en_US"
        self.lang_dir = Path("lang")

    def set_language(self, lang_code: str) -> None:
        """设置当前语言"""
        if lang_code == self._current_lang:
            return

        if self._load_lang_file(lang_code):
            self._current_lang = lang_code
        else:
            self._load_lang_file(self._fallback_lang)
            self._current_lang = self._fallback_lang

    def _load_lang_file(self, lang_code: str) -> bool:
        """加载语言文件"""
        lang_path = self.lang_dir / f"{lang_code}.yml"

        try:
            with open(lang_path, "r", encoding="utf-8") as f:
                self._translations = yaml.safe_load(f)
            return True
        except (FileNotFoundError, yaml.YAMLError) as e:
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
    """设置当前语言（全局快捷方式）"""
    i18n.set_language(lang_code)


def t(key: str, **kwargs) -> str:
    """获取翻译文本（全局快捷方式）"""
    return i18n.get(key, **kwargs)
