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
    
    def click_alipay_member(automation: AppAutomation) -> None:
        """点击'支付宝会员'。"""
        if automation.common_actions:
            print("尝试点击'支付宝会员'...")
            if not automation.common_actions.click_by_text("支付宝会员"):
                print("未找到文本'支付宝会员'，尝试其他方式...")
                if not automation.common_actions.click_by_description("支付宝会员"):
                    print("尝试通过坐标点击中上位置...")
                    automation.common_actions.click_by_coordinates(0.5, 0.3)
    
    def wait_for_member_page(automation: AppAutomation) -> None:
        """等待7秒钟，等进入子页面。"""
        if automation.common_actions:
            print("等待7秒钟，等进入子页面...")
            automation.common_actions.wait_seconds(7.0)
    
    def click_daily_checkin(automation: AppAutomation) -> None:
        """点击'每日签到'。"""
        if automation.common_actions:
            print("尝试点击'每日签到'...")
            if not automation.common_actions.click_by_text("每日签到"):
                print("未找到文本'每日签到'，尝试其他方式...")
                if not automation.common_actions.click_by_description("每日签到"):
                    print("尝试通过坐标点击中上位置...")
                    automation.common_actions.click_by_coordinates(0.5, 0.4)
    
    def wait_after_checkin(automation: AppAutomation) -> None:
        """休眠15秒钟。"""
        if automation.common_actions:
            print("休眠15秒钟...")
            automation.common_actions.wait_seconds(15.0)
    
    def go_back_home(automation: AppAutomation) -> None:
        """返回到手机的Home页面。"""
        if automation.common_actions:
            print("返回到手机的Home页面...")
            automation.common_actions.press_home()
    
    return AppConfig(
        name="支付宝",
        package_keyword="AlipayGphone",
        package_name=None,
        launch_timeout=10.0,
        post_launch_delay=5.0,
        steps=[
            click_my_tab,
            click_alipay_member,
            wait_for_member_page,
            click_daily_checkin,
            wait_after_checkin,
            go_back_home
        ]
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


def create_qishui_music_config() -> AppConfig:
    """创建汽水音乐应用配置。"""
    
    def click_welfare(automation: AppAutomation) -> None:
        """点击福利按钮或者文本。"""
        if automation.common_actions:
            print("尝试点击'福利'按钮或文本...")
            if not automation.common_actions.click_by_text("福利"):
                print("未找到文本'福利'，尝试其他方式...")
                if not automation.common_actions.click_by_description("福利"):
                    print("尝试通过坐标点击底部导航栏位置...")
                    automation.common_actions.click_by_coordinates(0.8, 0.95)
    
    def wait_after_welfare_5s(automation: AppAutomation) -> None:
        """进入福利页面后等待5秒钟。"""
        if automation.common_actions:
            print("进入福利页面后等待5秒钟...")
            automation.common_actions.wait_seconds(5.0)
    
    def wait_10s(automation: AppAutomation) -> None:
        """等待10秒钟。"""
        if automation.common_actions:
            print("等待10秒钟...")
            automation.common_actions.wait_seconds(10.0)
    
    def scroll_to_bottom(automation: AppAutomation) -> None:
        """滑动到页面最底部。"""
        if automation.common_actions:
            print("滑动到页面最底部...")
            for i in range(5):
                automation.common_actions.swipe_up()
                automation.common_actions.wait_seconds(1.0)
            print("已完成5次滑动操作，到达页面底部")
    
    def click_complete_button(automation: AppAutomation) -> None:
        """点击"连续刷视频赚金币"右边的"去完成"按钮。"""
        if automation.common_actions:
            print("尝试点击'去完成'按钮...")
            if not automation.common_actions.click_by_text("去完成"):
                print("未找到文本'去完成'，尝试其他方式...")
                if not automation.common_actions.click_by_description("去完成"):
                    print("尝试通过精确坐标点击...")
                    print("根据估算: x≈88% 屏幕宽度, y≈33% 屏幕高度")
                    automation.common_actions.click_by_coordinates(0.88, 0.33)
    
    return AppConfig(
        name="汽水音乐",
        package_keyword="luna.music",
        package_name=None,
        launch_timeout=10.0,
        post_launch_delay=10.0,
        steps=[
            click_welfare,
            wait_after_welfare_5s,
            scroll_to_bottom,
            click_complete_button,
            wait_10s
        ]
    )
