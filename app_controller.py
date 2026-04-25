"""应用级动作封装。"""

from __future__ import annotations

import uiautomator2 as u2


class AppController:
    """提供应用启停等操作。"""

    def __init__(self, device: u2.Device) -> None:
        self.d = device

    def start_app(self, package_name: str, wait: bool = True, timeout: float = 10) -> None:
        """启动应用。"""
        self.d.app_start(package_name, wait=wait)
        self.d.app_wait(package_name, timeout=timeout)

    def stop_app(self, package_name: str) -> None:
        """停止应用。"""
        self.d.app_stop(package_name)
