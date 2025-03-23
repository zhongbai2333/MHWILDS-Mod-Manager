import os
import shutil
import requests
import zipfile
import tempfile
from tqdm import tqdm
from urllib.parse import urlparse
from pathlib import Path
from typing import List, Dict, Union


from ..context import GlobalContext
from ..i18n import t


def download_with_progress(url: str, save_path: str) -> None:
    """
    带进度条的文件下载函数

    :param url: 下载链接
    :param save_path: 本地保存路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 发送HEAD请求获取文件大小
    with requests.head(url, allow_redirects=True) as response:
        response.raise_for_status()
        file_size = int(response.headers.get("Content-Length", 0))

    # 流式下载
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        # 初始化进度条
        progress = tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=f"Download {urlparse(url).path.split('/')[-1]}",
            ncols=100,  # 进度条宽度
        )

        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # 过滤保持连接的空白块
                    f.write(chunk)
                    progress.update(len(chunk))

        progress.close()

    # 验证下载完整性
    if file_size > 0 and os.path.getsize(save_path) != file_size:
        os.remove(save_path)
        raise IOError(t("downloader.download_vail_fail"))


class FileUpdater:
    def __init__(self):
        self._config = GlobalContext.get_config()
        self.logger = GlobalContext.get_logger()

    def install_from_zip(
        self,
        url: str,
        copy_rules: List[Dict[str, Union[str, bool]]],
        cleanup_patterns: List[str] = None,
    ) -> None:
        """
        通用安装方法

        :param url: 下载地址
        :param copy_rules: 复制规则 [
            {
                'src': '源相对路径',
                'dst': '目标相对路径',
                'overwrite': True/False,  # 可选，默认True
                'type': 'file/dir'  # 可选，自动检测
            }
        ]
        :param cleanup_patterns: 清理模式列表 ["*.tmp"]
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                zip_path = self._download_file(url, tmp_dir)
                extract_dir = self._extract_zip(zip_path, tmp_dir)
                self._copy_assets(extract_dir, copy_rules)
                self._cleanup_files(cleanup_patterns or [])

                self.logger.info(t("downloader.install_success"))
            except Exception as e:
                self.logger.error(t("downloader.install_failed", error=str(e)))
                raise

    def _download_file(self, url: str, save_dir: str) -> str:
        """文件下载方法"""
        self.logger.info(t("downloader.download_start", url=url))
        try:
            local_path = os.path.join(save_dir, "download.zip")
            download_with_progress(url, local_path)
            self.logger.info(t("downloader.download_success"))
            return local_path
        except requests.exceptions.RequestException as e:
            self.logger.error(t("downloader.download_failed", error=str(e)))
            raise RuntimeError(t("downloader.download_failed_short"))

    def _extract_zip(self, zip_path: str, extract_dir: str) -> str:
        """解压ZIP文件"""
        self.logger.info(t("downloader.unzip_start", path=zip_path))
        try:
            extract_folder = os.path.join(extract_dir, "extracted")
            os.makedirs(extract_folder, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_folder)

            self.logger.info(t("downloader.unzip_success"))
            return extract_folder

        except zipfile.BadZipFile as e:
            self.logger.error(t("downloader.unzip_fail"))
            raise RuntimeError(t("downloader.invalid_zip"))

    def _copy_assets(
        self, extract_dir: str, rules: List[Dict[str, Union[str, bool]]]
    ) -> None:
        """通用资源复制方法"""
        game_root = Path(self._config.game_path)
        src_root = Path(extract_dir)

        for rule in rules:
            try:
                src_path = src_root / rule["src"]
                dst_path = game_root / rule["dst"]

                # 自动检测类型
                is_dir = rule.get("type") == "dir" or src_path.is_dir()
                overwrite = rule.get("overwrite", True)

                if is_dir:
                    self._copy_directory(src_path, dst_path, overwrite)
                else:
                    self._copy_single_file(src_path, dst_path, overwrite)

            except Exception as e:
                self.logger.error(
                    t(
                        "downloader.copy_error",
                        src=str(src_path),
                        dst=str(dst_path),
                        error=str(e),
                    )
                )
                raise

    def _copy_directory(self, src: Path, dst: Path, overwrite: bool) -> None:
        """复制目录"""
        if dst.exists():
            if overwrite:
                self.logger.debug(t("downloader.overwriting_dir", path=str(dst)))
                shutil.rmtree(dst)
            else:
                self.logger.debug(t("downloader.skipping_dir", path=str(dst)))
                return

        shutil.copytree(src, dst)
        self.logger.info(t("downloader.copied_dir", src=str(src), dst=str(dst)))

    def _copy_single_file(self, src: Path, dst: Path, overwrite: bool) -> None:
        """复制单个文件"""
        if not src.exists():
            raise FileNotFoundError(t("downloader.source_missing", path=str(src)))

        if dst.exists():
            if overwrite:
                self.logger.debug(t("downloader.overwriting_file", path=str(dst)))
                dst.unlink()
            else:
                self.logger.debug(t("downloader.skipping_file", path=str(dst)))
                return

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        self.logger.info(t("downloader.copied_file", src=str(src), dst=str(dst)))

    def _cleanup_files(self, patterns: List[str]) -> None:
        """清理旧文件"""
        if not patterns:
            return

        self.logger.info(t("downloader.start_cleanup"))
        game_root = Path(self._config.game_path)

        for pattern in patterns:
            for path in game_root.glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                        self.logger.debug(t("downloader.cleaned_file", path=str(path)))
                    elif path.is_dir():
                        shutil.rmtree(path)
                        self.logger.debug(t("downloader.cleaned_dir", path=str(path)))
                except Exception as e:
                    self.logger.warning(
                        t("downloader.cleanup_failed", path=str(path), error=str(e))
                    )
