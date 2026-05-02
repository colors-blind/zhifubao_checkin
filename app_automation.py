"""
通用应用自动化测试流程抽象模块。

该模块提供了一个通用的 Android 应用自动化框架，基于 uiautomator2 库。
主要功能包括：
- 设备连接与管理
- 应用启动与停止
- 自定义自动化流程执行
- 内置多个应用的自动化配置（支付宝签到、微信、汽水音乐等）

核心设计理念：
1. 模块化设计：将设备管理、应用控制、通用操作分离
2. 配置驱动：通过 AppConfig 类定义自动化流程
3. 可扩展性：支持添加新的应用配置和操作步骤

使用示例：
    automation = AppAutomation()
    automation.connect_device()
    
    # 执行支付宝签到流程
    alipay_config = create_alipay_config()
    automation.run_app_flow(alipay_config)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import uiautomator2 as u2

from app_controller import AppController
from common_actions import CommonActions
from device_manager import DeviceManager


@dataclass
class AppConfig:
    """
    应用配置类，用于定义应用的基本信息和自动化流程。
    
    该类是一个数据容器，用于封装执行应用自动化所需的所有配置信息。
    通过 dataclass 装饰器实现简洁的初始化和属性管理。
    
    属性说明：
        name: 应用的显示名称，用于日志输出
        package_keyword: 应用包名的关键字，用于自动查找包名
        package_name: 应用的完整包名，如果为 None 则通过 package_keyword 自动查找
        launch_timeout: 启动应用时的超时时间（秒），默认 10.0 秒
        post_launch_delay: 应用启动后等待的时间（秒），用于等待界面加载完成，默认 5.0 秒
        steps: 自动化流程步骤列表，每个元素是一个可调用对象，接收 AppAutomation 实例作为参数
    
    使用示例：
        config = AppConfig(
            name="支付宝",
            package_keyword="AlipayGphone",
            steps=[step1, step2, step3]
        )
    """
    name: str
    package_keyword: str
    package_name: Optional[str] = None
    launch_timeout: float = 10.0
    post_launch_delay: float = 5.0
    steps: List[Callable] = field(default_factory=list)


class AppAutomation:
    """
    通用应用自动化测试流程管理器。
    
    该类是整个自动化框架的核心，负责协调设备连接、应用控制和自动化流程执行。
    
    主要职责：
    1. 管理设备连接生命周期
    2. 提供应用包名查找功能
    3. 执行预定义的自动化流程
    4. 处理异常情况和错误报告
    
    属性说明：
        device_manager: 设备管理器实例，负责设备连接和包名查找
        device: uiautomator2 设备对象，用于直接操作设备
        app_controller: 应用控制器实例，负责应用的启动和停止
        common_actions: 通用操作实例，封装了常见的 UI 操作
    
    使用示例：
        # 基本使用
        automation = AppAutomation()
        automation.connect_device()
        
        # 执行自动化流程
        config = create_alipay_config()
        automation.run_app_flow(config)
    """

    def __init__(self, device_serial: Optional[str] = None) -> None:
        """
        初始化 AppAutomation 实例。
        
        参数：
            device_serial: 可选的设备序列号，用于连接特定设备。
                          如果为 None，则自动连接第一个可用设备。
        
        初始化过程：
        1. 创建 DeviceManager 实例
        2. 初始化 device、app_controller、common_actions 为 None
           这些属性将在 connect_device() 方法调用时被赋值
        """
        self.device_manager = DeviceManager(device_serial)
        self.device: Optional[u2.Device] = None
        self.app_controller: Optional[AppController] = None
        self.common_actions: Optional[CommonActions] = None

    def connect_device(self) -> u2.Device:
        """
        连接设备并初始化控制器。
        
        该方法是使用自动化框架的第一步，必须在执行任何自动化操作之前调用。
        
        返回值：
            u2.Device: uiautomator2 设备对象，可用于直接操作设备
        
        执行步骤：
        1. 通过 DeviceManager 连接设备
        2. 使用设备对象初始化 AppController
        3. 使用设备对象初始化 CommonActions
        4. 输出连接成功信息
        
        异常处理：
            如果设备连接失败，将抛出 uiautomator2 相关异常
        """
        self.device = self.device_manager.connect()
        self.app_controller = AppController(self.device)
        self.common_actions = CommonActions(self.device)
        return self.device

    def find_app_package(self, keyword: str) -> Optional[str]:
        """
        通过关键字查找应用包名。
        
        该方法会在设备上安装的所有应用中查找第一个匹配指定关键字的包名。
        匹配是大小写不敏感的。
        
        参数：
            keyword: 要搜索的关键字，可以是包名的一部分
            
        返回值：
            Optional[str]: 找到的第一个匹配的包名，如果没有找到则返回 None
        
        使用示例：
            package = automation.find_app_package("AlipayGphone")
            if package:
                print(f"找到支付宝: {package}")
        """
        return self.device_manager.find_package_by_keyword(keyword)

    def find_all_app_packages(self, keyword: str) -> List[str]:
        """
        通过关键字查找所有匹配的应用包名。
        
        与 find_app_package 不同，该方法会返回所有匹配的包名列表。
        这在有多个应用包含相同关键字时很有用。
        
        参数：
            keyword: 要搜索的关键字，可以是包名的一部分
            
        返回值：
            List[str]: 所有匹配的包名列表，如果没有找到则返回空列表
        
        使用示例：
            packages = automation.find_all_app_packages("music")
            for pkg in packages:
                print(f"找到音乐应用: {pkg}")
        """
        return self.device_manager.find_packages_by_keyword(keyword)

    def launch_app(self, package_name: str, wait: bool = True, timeout: float = 10) -> None:
        """
        启动应用。
        
        通过包名启动指定的 Android 应用。该方法会等待应用完全启动后返回。
        
        参数：
            package_name: 要启动的应用包名
            wait: 是否等待应用启动完成，默认为 True
            timeout: 等待应用启动的超时时间（秒），默认为 10 秒
            
        注意事项：
            - 必须先调用 connect_device() 方法
            - 确保设备已连接且应用已安装
            - 如果 app_controller 未初始化，该方法将静默失败
        """
        if self.app_controller:
            self.app_controller.start_app(package_name, wait=wait, timeout=timeout)

    def stop_app(self, package_name: str) -> None:
        """
        停止应用。
        
        强制停止指定的应用。这相当于在设置中强制停止应用。
        
        参数：
            package_name: 要停止的应用包名
            
        注意事项：
            - 必须先调用 connect_device() 方法
            - 如果 app_controller 未初始化，该方法将静默失败
        """
        if self.app_controller:
            self.app_controller.stop_app(package_name)

    def run_app_flow(self, app_config: AppConfig) -> bool:
        """
        运行应用自动化流程。
        
        这是框架的核心方法，用于执行完整的应用自动化流程。
        流程包括：查找包名、启动应用、等待加载、执行步骤等。
        
        参数：
            app_config: 应用配置对象，包含包名信息和自动化步骤
            
        返回值：
            bool: 流程是否成功完成所有步骤
                - True: 所有步骤执行成功
                - False: 任何步骤失败或出现异常
        
        执行流程：
        1. 确保设备已连接（如果未连接则自动连接）
        2. 查找应用包名（如果未在配置中提供）
        3. 启动应用
        4. 等待应用加载完成
        5. 按顺序执行所有预定义的步骤
        6. 处理异常并返回结果
        
        错误处理：
            - 设备连接失败：返回 False
            - 应用未找到：返回 False
            - 应用启动失败：返回 False
            - 任何步骤执行失败：返回 False
            - 其他异常：返回 False 并打印错误信息
        
        日志输出：
            该方法会在每个关键步骤输出详细的日志信息，包括：
            - 正在查找的应用名称和关键字
            - 找到的应用包名
            - 正在启动的应用
            - 等待时间
            - 正在执行的步骤
            - 执行结果
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
    """
    创建支付宝应用配置。
    
    该函数创建一个预配置的 AppConfig 对象，用于执行支付宝的自动化签到流程。
    
    自动化流程步骤：
    1. click_my_tab: 点击右下角的"我的"标签
    2. click_alipay_member: 点击"支付宝会员"入口
    3. wait_for_member_page: 等待7秒钟，确保进入子页面
    4. click_daily_checkin: 点击"每日签到"按钮
    5. wait_after_checkin: 等待15秒钟，确保签到完成
    6. go_back_home: 返回到手机的主屏幕
    
    配置细节：
    - 应用名称：支付宝
    - 包名关键字：AlipayGphone（用于自动查找包名）
    - 启动超时：10秒
    - 启动后等待：5秒（等待应用完全加载）
    
    实现细节：
    每个步骤都是一个嵌套函数，接收 AppAutomation 实例作为参数。
    这些函数使用 common_actions 提供的方法执行具体操作。
    
    容错机制：
    每个点击操作都有多重备选方案：
    1. 首先尝试通过文本点击（click_by_text）
    2. 如果失败，尝试通过描述点击（click_by_description）
    3. 如果都失败，尝试通过坐标点击（click_by_coordinates）
    
    返回值：
        AppConfig: 配置好的支付宝应用配置对象
        
    使用示例：
        automation = AppAutomation()
        automation.connect_device()
        config = create_alipay_config()
        automation.run_app_flow(config)
    """
    
    def click_my_tab(automation: AppAutomation) -> None:
        """
        点击右下角的"我的"标签。
        
        这是支付宝签到流程的第一步，用于切换到"我的"页面。
        
        执行策略：
        1. 首先尝试通过文本"我的"找到并点击该元素
        2. 如果文本点击失败，尝试通过 content-description "我的"点击
        3. 如果以上都失败，尝试通过相对坐标 (0.85, 0.95) 点击
           （通常对应屏幕右下角区域）
        
        参数：
            automation: AppAutomation 实例，提供 common_actions 操作
        """
        if automation.common_actions:
            print("尝试点击'我的'...")
            if not automation.common_actions.click_by_text("我的"):
                print("未找到文本'我的'，尝试其他方式...")
                if not automation.common_actions.click_by_description("我的"):
                    print("尝试通过坐标点击右下角...")
                    automation.common_actions.click_by_coordinates(0.85, 0.95)
    
    def click_alipay_member(automation: AppAutomation) -> None:
        """
        点击"支付宝会员"入口。
        
        这是签到流程的第二步，用于进入支付宝会员页面。
        
        执行策略：
        1. 首先尝试通过文本"支付宝会员"找到并点击
        2. 如果文本点击失败，尝试通过 content-description 点击
        3. 如果都失败，尝试通过相对坐标 (0.5, 0.3) 点击
           （通常对应屏幕中上位置）
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("尝试点击'支付宝会员'...")
            if not automation.common_actions.click_by_text("支付宝会员"):
                print("未找到文本'支付宝会员'，尝试其他方式...")
                if not automation.common_actions.click_by_description("支付宝会员"):
                    print("尝试通过坐标点击中上位置...")
                    automation.common_actions.click_by_coordinates(0.5, 0.3)
    
    def wait_for_member_page(automation: AppAutomation) -> None:
        """
        等待7秒钟，确保进入支付宝会员子页面。
        
        这是一个纯等待步骤，用于给页面足够的加载时间。
        因为从"我的"页面点击"支付宝会员"后，页面可能需要动画过渡和数据加载。
        
        等待时间：7秒
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("等待7秒钟，等进入子页面...")
            automation.common_actions.wait_seconds(7.0)
    
    def click_daily_checkin(automation: AppAutomation) -> None:
        """
        点击"每日签到"按钮。
        
        这是签到流程的核心步骤，用于完成每日签到操作。
        
        执行策略：
        1. 首先尝试通过文本"每日签到"找到并点击
        2. 如果文本点击失败，尝试通过 content-description 点击
        3. 如果都失败，尝试通过相对坐标 (0.5, 0.4) 点击
           （通常对应屏幕中上偏下的位置）
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("尝试点击'每日签到'...")
            if not automation.common_actions.click_by_text("每日签到"):
                print("未找到文本'每日签到'，尝试其他方式...")
                if not automation.common_actions.click_by_description("每日签到"):
                    print("尝试通过坐标点击中上位置...")
                    automation.common_actions.click_by_coordinates(0.5, 0.4)
    
    def wait_after_checkin(automation: AppAutomation) -> None:
        """
        签到后等待15秒钟。
        
        这是签到后的等待步骤，目的是：
        1. 等待签到操作完成
        2. 等待可能出现的奖励弹窗显示
        3. 确保所有后台操作完成
        
        等待时间：15秒
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("休眠15秒钟...")
            automation.common_actions.wait_seconds(15.0)
    
    def go_back_home(automation: AppAutomation) -> None:
        """
        返回到手机的主屏幕。
        
        这是整个自动化流程的最后一步，用于：
        1. 退出当前应用
        2. 将设备恢复到初始状态
        3. 为下一次自动化操作做好准备
        
        实现方式：模拟按下 HOME 键
        
        参数：
            automation: AppAutomation 实例
        """
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
    """
    创建微信应用配置（示例）。
    
    这是一个示例配置，展示如何为微信创建自动化流程。
    当前只包含一个简单的步骤：点击"我"标签。
    
    这个配置可以作为参考，用于扩展更多微信自动化功能，例如：
    - 微信运动步数同步
    - 微信支付自动化
    - 微信消息自动回复等
    
    配置细节：
    - 应用名称：微信
    - 包名关键字：mm（微信包名通常包含 mm）
    - 启动超时：10秒
    - 启动后等待：5秒
    
    返回值：
        AppConfig: 配置好的微信应用配置对象
        
    使用示例：
        automation = AppAutomation()
        automation.connect_device()
        config = create_wechat_config()
        automation.run_app_flow(config)
    """
    
    def click_me_tab(automation: AppAutomation) -> None:
        """
        点击右下角的"我"标签。
        
        这是微信界面的常用入口，从这里可以访问：
        - 个人信息
        - 支付功能
        - 收藏
        - 设置等
        
        执行策略：
        1. 首先尝试通过文本"我"找到并点击
        2. 如果失败，尝试通过相对坐标 (0.85, 0.95) 点击
           （通常对应屏幕右下角区域）
        
        参数：
            automation: AppAutomation 实例
        """
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
    """
    创建汽水音乐应用配置。
    
    该函数创建一个预配置的 AppConfig 对象，用于执行汽水音乐的自动化操作。
    主要目的是自动完成任务以赚取金币或积分。
    
    汽水音乐是字节跳动旗下的音乐应用，通常有刷视频赚金币的活动。
    这个配置自动执行以下步骤：
    
    自动化流程步骤：
    1. click_welfare: 点击"福利"按钮，进入福利页面
    2. wait_after_welfare_5s: 进入福利页面后等待5秒
    3. scroll_to_bottom: 滑动到页面最底部（执行5次上滑）
    4. click_complete_button: 点击"去完成"按钮
    5. wait_10s: 最后等待10秒
    
    配置细节：
    - 应用名称：汽水音乐
    - 包名关键字：luna.music（汽水音乐的包名包含此关键字）
    - 启动超时：10秒
    - 启动后等待：10秒（汽水音乐启动较慢）
    
    注意事项：
    - 汽水音乐的界面可能会随版本更新而变化
    - 坐标点击是备选方案，可能需要根据实际屏幕调整
    - 滑动操作是为了浏览页面内容，触发金币奖励
    
    返回值：
        AppConfig: 配置好的汽水音乐应用配置对象
        
    使用示例：
        automation = AppAutomation()
        automation.connect_device()
        config = create_qishui_music_config()
        automation.run_app_flow(config)
    """
    
    def click_welfare(automation: AppAutomation) -> None:
        """
        点击福利按钮或者文本。
        
        汽水音乐的福利页面通常包含金币任务、签到等功能入口。
        这是自动化流程的第一步。
        
        执行策略：
        1. 首先尝试通过文本"福利"找到并点击
        2. 如果文本点击失败，尝试通过 content-description 点击
        3. 如果都失败，尝试通过相对坐标 (0.8, 0.95) 点击
           （通常对应底部导航栏右侧位置）
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("尝试点击'福利'按钮或文本...")
            if not automation.common_actions.click_by_text("福利"):
                print("未找到文本'福利'，尝试其他方式...")
                if not automation.common_actions.click_by_description("福利"):
                    print("尝试通过坐标点击底部导航栏位置...")
                    automation.common_actions.click_by_coordinates(0.8, 0.95)
    
    def wait_after_welfare_5s(automation: AppAutomation) -> None:
        """
        进入福利页面后等待5秒钟。
        
        目的是等待页面完全加载，包括：
        - 任务列表加载
        - 金币数据刷新
        - 页面动画完成
        
        等待时间：5秒
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("进入福利页面后等待5秒钟...")
            automation.common_actions.wait_seconds(5.0)
    
    def wait_10s(automation: AppAutomation) -> None:
        """
        等待10秒钟。
        
        这是一个通用的等待步骤，用于：
        - 等待任务页面加载
        - 等待操作完成
        - 给系统足够的响应时间
        
        等待时间：10秒
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("等待10秒钟...")
            automation.common_actions.wait_seconds(10.0)
    
    def scroll_to_bottom(automation: AppAutomation) -> None:
        """
        滑动到页面最底部。
        
        执行5次向上滑动操作，目的是：
        1. 浏览页面内容，触发页面刷新
        2. 加载更多内容
        3. 找到可能在页面下方的任务按钮
        
        实现细节：
        - 每次滑动后等待1秒，让页面有时间响应
        - 共执行5次滑动操作
        - 使用 swipe_up() 方法从屏幕中下方向上滑动
        
        参数：
            automation: AppAutomation 实例
        """
        if automation.common_actions:
            print("滑动到页面最底部...")
            for i in range(5):
                automation.common_actions.swipe_up()
                automation.common_actions.wait_seconds(1.0)
            print("已完成5次滑动操作，到达页面底部")
    
    def click_complete_button(automation: AppAutomation) -> None:
        """
        点击"连续刷视频赚金币"右边的"去完成"按钮。
        
        这是汽水音乐中常见的任务类型，点击"去完成"后通常会：
        - 跳转到视频播放页面
        - 开始自动播放视频
        - 累计观看时间以赚取金币
        
        执行策略：
        1. 首先尝试通过文本"去完成"找到并点击
        2. 如果文本点击失败，尝试通过 content-description 点击
        3. 如果都失败，尝试通过相对坐标 (0.88, 0.33) 点击
           （根据估算：x≈88% 屏幕宽度, y≈33% 屏幕高度）
        
        注意：
        - 页面上可能有多个"去完成"按钮
        - click_by_text 会点击第一个找到的匹配元素
        - 坐标值是估算值，可能需要根据实际界面调整
        
        参数：
            automation: AppAutomation 实例
        """
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
