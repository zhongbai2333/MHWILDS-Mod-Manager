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

    def _get_release_list(self) -> None:
        """初始化ref版本列表文件"""
        try:
            # 发送 GET 请求（添加 User-Agent 是 GitHub API 的要求）
            response = requests.get(
                self._url, headers={"User-Agent": "Mozilla/5.0"}
            )

            # 检查响应状态码
            if response.status_code == 200:
                self._releases = response.json()

                if not self._releases:
                    self._log_system.warning(t("github.cant_get_release"))
                    return

                latest_release = self._releases[0]
                latest_version = self._extract_version(latest_release.get('tag_name', None))
                now_verison = self._extract_version(self._config.installed_rf_version)

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
            print(f"请求发生错误: {str(e)}")
        except json.JSONDecodeError:
            print("响应内容不是有效的 JSON 格式")

    def _extract_version(self, tag) -> int:
        if not tag:
            return
        parts = tag.split("-")
        # 确保分割后至少有3部分：["nightly", "01090", "commit_hash"]
        if len(parts) >= 3 and parts[1].isdigit():
            return int(parts[1])
        else:
            raise ValueError(f"无效的版本标签格式: {tag}")
