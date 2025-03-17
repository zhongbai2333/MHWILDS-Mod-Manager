import logging
import zipfile
import datetime
import atexit
import time
import shutil
from pathlib import Path
from logging.handlers import RotatingFileHandler
from logging import Formatter


class ColoredMultiLineFormatter(Formatter):
    """支持颜色和多行对齐的日志格式化器"""

    COLOR_CODES = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[1;31m",  # 加粗红色
    }
    RESET_CODE = "\033[0m"

    def __init__(self, use_color=False):
        super().__init__()
        self.use_color = use_color

    def _colorize_level(self, level_name):
        """为日志级别添加颜色"""
        if self.use_color and level_name in self.COLOR_CODES:
            return f"{self.COLOR_CODES[level_name]}{level_name}{self.RESET_CODE}"
        return level_name

    def format(self, record):
        """核心格式化方法"""
        # 生成基础组件
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        colored_level = self._colorize_level(record.levelname)
        thread_name = record.threadName

        # 构建前缀模板
        header_prefix = f"[{timestamp}][{colored_level}][{thread_name}]"
        plain_prefix = f"[{timestamp}][{record.levelname}][{thread_name}]"
        line_prefix = " " * len(plain_prefix)  # 基于无颜色文本计算空格

        # 处理消息内容
        message = super().format(record)
        lines = message.splitlines()

        # 重组多行内容
        formatted_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                formatted_lines.append(f"{header_prefix} {line}")
            else:
                formatted_lines.append(f"{line_prefix} {line}")

        return "\n".join(formatted_lines)


class LogSystem(object):
    def __init__(self, debug: bool = False):
        self.logs_dir = Path("logs")
        self.latest_log = self.logs_dir / "latest.log"
        self.debug = debug
        self._setup_directories()
        self._configure_logging()
        atexit.register(self.safe_exit)

    def _setup_directories(self):
        """创建日志目录并清理空文件"""
        self.logs_dir.mkdir(exist_ok=True)
        # 清理可能存在的空文件
        if self.latest_log.exists() and self.latest_log.stat().st_size == 0:
            self.latest_log.unlink()

    def _configure_logging(self):
        """配置日志系统"""
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False  # 防止重复日志

        # 文件处理器（无颜色）
        file_formatter = ColoredMultiLineFormatter(use_color=False)
        self.file_handler = RotatingFileHandler(
            self.latest_log,
            maxBytes=10*1024*1024,
            backupCount=0,
            encoding='utf-8',
            delay=True
        )
        self.file_handler.setFormatter(file_formatter)
        self.file_handler.setLevel(logging.DEBUG)

        # 控制台处理器（带颜色）
        console_formatter = ColoredMultiLineFormatter(use_color=True)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG if self.debug else logging.INFO)

        # 添加处理器
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(console_handler)

    def safe_exit(self):
        """安全退出处理"""
        try:
            # 关闭所有日志处理器
            self._close_handlers()
            # 等待文件句柄释放
            time.sleep(0.5)
            # 执行归档
            self.archive_logs()
        except Exception as e:
            print(f"退出处理失败: {str(e)}")

    def _close_handlers(self):
        """关闭并移除所有文件处理器"""
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self.logger.removeHandler(handler)
        logging.shutdown()

    def archive_logs(self):
        """安全归档日志文件"""
        if not self.latest_log.exists() or self.latest_log.stat().st_size == 0:
            return

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"log_{timestamp}.zip"
            archive_path = self.logs_dir / archive_name

            # 使用临时副本进行压缩
            temp_log = self.logs_dir / f"temp_{timestamp}.log"
            shutil.copyfile(self.latest_log, temp_log)

            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_log, arcname=f"{timestamp}.log")

            temp_log.unlink()
            self.latest_log.unlink()
            print(f"日志已归档至: {archive_path}")

        except Exception as e:
            print(f"归档日志失败: {str(e)}")
            # 保留日志文件供下次启动处理
            if temp_log.exists():
                temp_log.unlink()
