"""设备连接与基础信息管理。"""

from __future__ import annotations

import re
import subprocess
from typing import List, Optional

import uiautomator2 as u2


class DeviceManager:
    """负责连接 Android 设备并返回 uiautomator2 设备对象。"""

    def __init__(self, serial: str | None = None) -> None:
        self.serial = serial

    def connect(self) -> u2.Device:
        """连接设备。"""
        return u2.connect(self.serial) if self.serial else u2.connect()

    def get_installed_packages(self) -> List[str]:
        """获取设备上所有已安装的应用包名列表。"""
        cmd = ["adb"]
        if self.serial:
            cmd.extend(["-s", self.serial])
        cmd.extend(["shell", "pm", "list", "packages"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        packages = []
        
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("package:"):
                    package_name = line.split(":", 1)[1].strip()
                    packages.append(package_name)
        
        return packages

    def find_package_by_keyword(self, keyword: str) -> Optional[str]:
        """
        通过关键字模糊查找应用包名。
        返回第一个匹配的包名，如果没有匹配则返回 None。
        """
        packages = self.get_installed_packages()
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        for package in packages:
            if pattern.search(package):
                return package
        
        return None

    def find_packages_by_keyword(self, keyword: str) -> List[str]:
        """
        通过关键字模糊查找所有匹配的应用包名。
        返回所有匹配的包名列表。
        """
        packages = self.get_installed_packages()
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        matched_packages = []
        for package in packages:
            if pattern.search(package):
                matched_packages.append(package)
        
        return matched_packages
