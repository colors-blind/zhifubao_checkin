"""常用动作封装。"""

from __future__ import annotations

import time

import uiautomator2 as u2


class CommonActions:
    """对常见 UI 操作进行简单封装。"""

    def __init__(self, device: u2.Device) -> None:
        self.d = device

    def click_if_exists(self, timeout: float = 3, **selector: str) -> bool:
        """元素存在则点击并返回 True，否则返回 False。"""
        obj = self.d(**selector)
        if obj.wait(timeout=timeout):
            obj.click()
            return True
        return False

    def input_text(self, text: str, clear: bool = True, **selector: str) -> bool:
        """向指定元素输入文本。"""
        obj = self.d(**selector)
        if not obj.exists:
            return False
        if clear:
            obj.clear_text()
        obj.set_text(text)
        return True

    def wait_seconds(self, seconds: float) -> None:
        """显式等待。"""
        time.sleep(seconds)

    def press_back(self) -> None:
        """执行返回键。"""
        self.d.press("back")
