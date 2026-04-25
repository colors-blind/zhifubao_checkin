"""设备连接与基础信息管理。"""

from __future__ import annotations

import uiautomator2 as u2


class DeviceManager:
    """负责连接 Android 设备并返回 uiautomator2 设备对象。"""

    def __init__(self, serial: str | None = None) -> None:
        self.serial = serial

    def connect(self) -> u2.Device:
        """连接设备。"""
        return u2.connect(self.serial) if self.serial else u2.connect()
