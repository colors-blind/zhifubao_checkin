"""通用应用自动化测试流程抽象。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import uiautomator2 as u2

from app_controller import AppController
from common_actions import CommonActions
from device_manager import DeviceManager


@dataclass
class AppConfig:
    """应用配置类，用于定义应用的基本信息和自动化流程。"""
    name: str
    package_keyword: str
    package_name: Optional[str] = None
    launch_timeout: float = 10.0
    post_launch_delay: float = 5.0
    steps: List[Callable] = field(default_factory=list)


class AppAutomation:
    """通用应用自动化测试流程管理器。"""

    def __init__(self, device_serial: Optional[str] = None) -> None:
        self.device_manager = DeviceManager(device_serial)
        self.device: Optional[u2.Device] = None
        self.app_controller: Optional[AppController] = None
        self.common_actions: Optional[CommonActions] = None

    def connect_device(self) -> u2.Device:
        """连接设备并初始化控制器。"""
        self.device = self.device_manager.connect()
        self.app_controller = AppController(self.device)
        self.common_actions = CommonActions(self.device)
        return self.device

    def find_app_package(self, keyword: str) -> Optional[str]:
        """通过关键字查找应用包名。"""
        return self.device_manager.find_package_by_keyword(keyword)

    def find_all_app_packages(self, keyword: str) -> List[str]:
        """通过关键字查找所有匹配的应用包名。"""
        return self.device_manager.find_packages_by_keyword(keyword)

    def launch_app(self, package_name: str, wait: bool = True, timeout: float = 10) -> None:
        """启动应用。"""
        if self.app_controller:
            self.app_controller.start_app(package_name, wait=wait, timeout=timeout)

    def stop_app(self, package_name: str) -> None:
        """停止应用。"""
        if self.app_controller:
            self.app_controller.stop_app(package_name)

    def run_app_flow(self, app_config: AppConfig) -> bool:
        """
        运行应用自动化流程。
        
        流程：
        1. 查找应用包名（如果未提供）
        2. 启动应用
        3. 等待指定时间
        4. 执行预定义的步骤
        
        返回是否成功完成所有步骤。
        """
        if not self.device:
            self.connect_device()

        if not app_config.package_name:
            print(f"正在查找应用: {app_config.name} (关键字: {app_config.package_keyword})")
            app_config.package_name = self.find_app_package(app_config.package_keyword)
            
            if not app_config.package_name:
                print(f"错误: 未找到匹配关键字 '{app_config.package_keyword}' 的应用")
                return False
            
            print(f"找到应用包名: {app_config.package_name}")

        try:
            print(f"正在启动应用: {app_config.name}")
            self.launch_app(app_config.package_name, timeout=app_config.launch_timeout)
            print(f"应用已启动，等待 {app_config.post_launch_delay} 秒...")
            
            if self.common_actions:
                self.common_actions.wait_seconds(app_config.post_launch_delay)
            
            print("开始执行自动化步骤...")
            for i, step in enumerate(app_config.steps, 1):
                print(f"执行步骤 {i}: {step.__name__ if hasattr(step, '__name__') else '匿名函数'}")
                try:
                    step(self)
                except Exception as e:
                    print(f"步骤 {i} 执行失败: {e}")
                    return False
            
            print("自动化流程执行完成！")
            return True
            
        except Exception as e:
            print(f"自动化流程执行失败: {e}")
            return False


def create_alipay_config() -> AppConfig:
    """创建支付宝应用配置。"""
    
    def click_my_tab(automation: AppAutomation) -> None:
        """点击右下角的'我的'标签。"""
        if automation.common_actions:
            print("尝试点击'我的'...")
            if not automation.common_actions.click_by_text("我的"):
                print("未找到文本'我的'，尝试其他方式...")
                if not automation.common_actions.click_by_description("我的"):
                    print("尝试通过坐标点击右下角...")
                    automation.common_actions.click_by_coordinates(0.85, 0.95)
    
    return AppConfig(
        name="支付宝",
        package_keyword="AlipayGphone",
        package_name=None,
        launch_timeout=10.0,
        post_launch_delay=5.0,
        steps=[click_my_tab]
    )


def create_wechat_config() -> AppConfig:
    """创建微信应用配置（示例）。"""
    
    def click_me_tab(automation: AppAutomation) -> None:
        """点击右下角的'我'标签。"""
        if automation.common_actions:
            print("尝试点击'我'...")
            if not automation.common_actions.click_by_text("我"):
                automation.common_actions.click_by_coordinates(0.85, 0.95)
    
    return AppConfig(
        name="微信",
        package_keyword="mm",
        package_name=None,
        launch_timeout=10.0,
        post_launch_delay=5.0,
        steps=[click_me_tab]
    )
