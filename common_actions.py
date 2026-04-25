"""常用动作封装。"""

from __future__ import annotations

import time
from typing import Optional, Tuple

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

    def click_by_text(self, text: str, timeout: float = 3) -> bool:
        """通过文本点击元素。"""
        return self.click_if_exists(timeout=timeout, text=text)

    def click_by_description(self, description: str, timeout: float = 3) -> bool:
        """通过 content-description 点击元素。"""
        return self.click_if_exists(timeout=timeout, description=description)

    def click_by_resource_id(self, resource_id: str, timeout: float = 3) -> bool:
        """通过 resource-id 点击元素。"""
        return self.click_if_exists(timeout=timeout, resourceId=resource_id)

    def click_by_coordinates(self, x: float, y: float) -> None:
        """通过坐标点击屏幕。坐标为相对坐标 (0.0-1.0) 或绝对坐标。"""
        if 0 <= x <= 1 and 0 <= y <= 1:
            self.d.click(x, y)
        else:
            self.d.click(int(x), int(y))

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

    def wait_for_element(self, timeout: float = 10, **selector: str) -> bool:
        """等待元素出现，返回是否成功。"""
        obj = self.d(**selector)
        return obj.wait(timeout=timeout)

    def wait_for_element_gone(self, timeout: float = 10, **selector: str) -> bool:
        """等待元素消失，返回是否成功。"""
        obj = self.d(**selector)
        return obj.wait_gone(timeout=timeout)

    def press_back(self) -> None:
        """执行返回键。"""
        self.d.press("back")

    def press_home(self) -> None:
        """执行主页键。"""
        self.d.press("home")

    def press_recent(self) -> None:
        """执行最近应用键。"""
        self.d.press("recent")

    def screenshot(self, filename: str) -> None:
        """截图并保存到指定文件。"""
        self.d.screenshot(filename)

    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸 (宽度, 高度)。"""
        return self.d.window_size()

    def swipe(self, start_x: float, start_y: float, end_x: float, end_y: float, duration: float = 0.5) -> None:
        """滑动屏幕。坐标为相对坐标 (0.0-1.0) 或绝对坐标。"""
        if all(0 <= coord <= 1 for coord in [start_x, start_y, end_x, end_y]):
            self.d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        else:
            self.d.swipe(int(start_x), int(start_y), int(end_x), int(end_y), duration=duration)

    def swipe_up(self, duration: float = 0.5) -> None:
        """向上滑动屏幕。"""
        width, height = self.get_screen_size()
        self.swipe(width / 2, height * 0.8, width / 2, height * 0.2, duration)

    def swipe_down(self, duration: float = 0.5) -> None:
        """向下滑动屏幕。"""
        width, height = self.get_screen_size()
        self.swipe(width / 2, height * 0.2, width / 2, height * 0.8, duration)

    def swipe_left(self, duration: float = 0.5) -> None:
        """向左滑动屏幕。"""
        width, height = self.get_screen_size()
        self.swipe(width * 0.8, height / 2, width * 0.2, height / 2, duration)

    def swipe_right(self, duration: float = 0.5) -> None:
        """向右滑动屏幕。"""
        width, height = self.get_screen_size()
        self.swipe(width * 0.2, height / 2, width * 0.8, height / 2, duration)
