"""
应用级动作封装模块。

该模块提供了 AppController 类，用于封装 Android 应用的启停操作。
它是整个自动化框架中负责应用生命周期管理的核心组件。

主要功能：
- 启动应用：通过包名启动指定的 Android 应用
- 停止应用：强制停止指定的 Android 应用
- 等待应用启动：确保应用完全启动后再进行后续操作

设计理念：
- 单一职责：只负责应用的启动和停止，不涉及具体的 UI 操作
- 简洁封装：对 uiautomator2 的底层 API 进行简单封装，提供更友好的接口
- 可靠性：包含等待机制，确保应用启动完成后再返回

依赖关系：
- 依赖 uiautomator2 库提供底层设备操作能力
- 被 AppAutomation 类使用，作为应用控制的代理

使用示例：
    import uiautomator2 as u2
    
    # 连接设备
    device = u2.connect()
    
    # 创建应用控制器
    controller = AppController(device)
    
    # 启动应用
    controller.start_app("com.eg.android.AlipayGphone", wait=True, timeout=10)
    
    # 停止应用
    controller.stop_app("com.eg.android.AlipayGphone")

注意事项：
- 必须先连接设备，获得 u2.Device 对象后才能使用
- 应用包名必须准确，否则启动会失败
- 超时时间应根据应用启动速度合理设置
"""

from __future__ import annotations

import uiautomator2 as u2


class AppController:
    """
    应用控制器类，提供应用启停等操作。
    
    该类封装了 Android 应用的启动和停止操作，是连接 uiautomator2 底层 API
    与上层自动化逻辑的桥梁。
    
    属性说明：
        d: uiautomator2 的 Device 对象，用于执行实际的设备操作
    
    设计特点：
    1. 轻量级封装：只提供最核心的应用控制功能
    2. 可靠等待：启动应用时包含等待机制，确保应用完全启动
    3. 异常传递：底层异常直接向上抛出，由上层处理
    
    使用场景：
    - 自动化测试前启动目标应用
    - 测试完成后清理应用进程
    - 多应用切换场景下的应用管理
    
    与其他组件的关系：
    - 被 AppAutomation 类持有和使用
    - 依赖 DeviceManager 连接的设备
    - 不直接依赖 CommonActions，各司其职
    """

    def __init__(self, device: u2.Device) -> None:
        """
        初始化 AppController 实例。
        
        参数：
            device: uiautomator2 的 Device 对象，必须是已连接的有效设备
            
        初始化过程：
        1. 保存传入的设备对象到实例变量 d
        2. 该设备对象将用于后续所有应用控制操作
        
        注意事项：
            - 传入的 device 必须是已经成功连接的设备对象
            - 如果 device 无效，后续操作将抛出异常
            - 建议通过 DeviceManager 类获取设备对象
            
        使用示例：
            import uiautomator2 as u2
            
            # 方式1：直接连接设备
            device = u2.connect()
            controller = AppController(device)
            
            # 方式2：通过 DeviceManager（推荐）
            from device_manager import DeviceManager
            dm = DeviceManager()
            device = dm.connect()
            controller = AppController(device)
        """
        self.d = device

    def start_app(self, package_name: str, wait: bool = True, timeout: float = 10) -> None:
        """
        启动应用。
        
        通过包名启动指定的 Android 应用，并可选择等待应用完全启动。
        
        参数：
            package_name: 要启动的应用包名，例如 "com.eg.android.AlipayGphone"
            wait: 是否等待应用启动完成，默认为 True
                  - True: 会调用 app_wait() 等待应用启动
                  - False: 启动后立即返回，不等待
            timeout: 等待应用启动的超时时间（秒），默认为 10 秒
                     仅在 wait=True 时有效
                     
        执行流程：
        1. 调用 uiautomator2 的 app_start() 方法启动应用
        2. 如果 wait=True，调用 app_wait() 等待应用启动完成
        3. 如果超时，uiautomator2 会抛出超时异常
        
        异常处理：
            - 包名不存在：uiautomator2 会抛出相关异常
            - 超时：如果 wait=True 且应用在超时时间内未启动，会抛出超时异常
            - 设备断开：如果设备连接中断，会抛出连接异常
            
        使用示例：
            # 基本使用（等待启动）
            controller.start_app("com.eg.android.AlipayGphone")
            
            # 不等待启动
            controller.start_app("com.tencent.mm", wait=False)
            
            # 自定义超时时间
            controller.start_app("com.ss.android.ugc.aweme", timeout=15)
            
        注意事项：
            - 确保设备已解锁，否则应用可能无法正常启动
            - 部分应用启动较慢，可能需要适当增加超时时间
            - 如果应用已经在运行，调用此方法会将其切换到前台
        """
        self.d.app_start(package_name, wait=wait)
        self.d.app_wait(package_name, timeout=timeout)

    def stop_app(self, package_name: str) -> None:
        """
        停止应用。
        
        强制停止指定的 Android 应用。这相当于在系统设置中点击"强制停止"。
        
        参数：
            package_name: 要停止的应用包名
            
        执行效果：
            - 应用的所有进程都会被杀死
            - 应用的所有活动都会被销毁
            - 应用的后台服务也会被停止
            - 不会清除应用数据（与"清除数据"不同）
            
        使用场景：
            1. 测试开始前，确保应用处于初始状态
            2. 测试结束后，清理后台进程
            3. 应用出现异常时，强制重启应用
            
        使用示例：
            # 停止支付宝
            controller.stop_app("com.eg.android.AlipayGphone")
            
            # 停止微信
            controller.stop_app("com.tencent.mm")
            
        注意事项：
            - 即使应用当前未运行，调用此方法也不会报错
            - 系统应用可能无法被普通用户停止
            - 停止应用后，再次启动需要重新初始化所有状态
            
        与返回键的区别：
            - 返回键：只是退出当前 Activity，应用可能仍在后台运行
            - stop_app：完全终止应用进程，所有状态都会被清除
        """
        self.d.app_stop(package_name)
