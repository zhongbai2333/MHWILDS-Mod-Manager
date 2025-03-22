import json
import requests

from ..context import GlobalContext
from ..i18n import t


class RefManage(object):
    def __init__(self):
        self._log_system = GlobalContext.get_logger()
        self._config = GlobalContext.get_config()
        self._url = "https://api.github.com/repos/praydog/REFramework-nightly/releases"
        self._releases = None
        self._get_release_list()

    def get_release_list_all_page(self, one_page: int) -> int:
        """以一页 one_page 个获取全部页码"""
        return len(self._releases) // one_page + (
            1 if len(self._releases) % one_page else 0
        )

    def get_release_list_page(self, one_page: int, page: int) -> list:
        """以每页 one_page 个的格式返回Release列表"""
        release_list = []
        for release in self._releases[(page - 1) * one_page : page * one_page]:
            release_list.append(
                [
                    release.get("name", None),
                    str(self.extract_version(release.get("tag_name", None))),
                    release.get("tag_name", None),
                    release.get("published_at", None),
                    release.get("assets", None)[3]
                    .get("browser_download_url", None),
                ]
            )
        return release_list

    def search_release(self, version) -> list:
        """搜索realse"""
        # 将目标版本号转换为整数
        try:
            target = int(version)
        except ValueError:
            raise ValueError("目标版本号必须是数字字符串或整数")

        for item in self._releases:
            try:
                current_version = self.extract_version(item["tag_name"])
                if current_version == target:
                    return [
                        item.get("name", None),
                        str(self.extract_version(item.get("tag_name", None))),
                        item.get("tag_name", None),
                        item.get("published_at", None),
                        item.get("assets", None)[3].get("browser_download_url", None),
                    ]
            except ValueError:
                continue  # 跳过无法提取版本号的项
        return None  # 未找到匹配项

    def install_ref(self) -> None:
        pass

    def uninstall_ref(self) -> None:
        pass

    def _get_release_list(self) -> None:
        """初始化ref版本列表文件"""
        try:
            # 发送 GET 请求（添加 User-Agent 是 GitHub API 的要求）
            response = requests.get(self._url, headers={"User-Agent": "Mozilla/5.0"})

            # 检查响应状态码
            if response.status_code == 200:
                self._releases = response.json()

                self._log_system.info(t("cli.ref_getted"))

                if not self._releases:
                    self._log_system.warning(t("github.cant_get_release"))
                    return

                latest_release = self._releases[0]
                latest_version = self.extract_version(
                    latest_release.get("tag_name", None)
                )
                now_verison = self.extract_version(self._config.installed_ref_version)

                if not now_verison:
                    return

                if latest_version > now_verison:
                    self._log_system.warning(
                        t(
                            "github.need_update",
                            latest_version=latest_version,
                            version=now_verison,
                        )
                    )

            else:
                self._log_system.error(
                    t(
                        "github.cant_get",
                        code=response.status_code,
                        reason=response.text,
                    )
                )

        except requests.exceptions.RequestException as e:
            self._log_system.error(t("github.get_error", reason=str(e)))
        except json.JSONDecodeError:
            self._log_system.error(t("github.json.error"))

    def extract_version(self, tag) -> int:
        if not tag:
            return
        parts = tag.split("-")
        # 确保分割后至少有3部分：["nightly", "01090", "commit_hash"]
        if len(parts) >= 3 and parts[1].isdigit():
            return int(parts[1])
        else:
            raise ValueError(f"无效的版本标签格式: {tag}")
